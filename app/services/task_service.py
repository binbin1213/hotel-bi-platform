from typing import Dict, List, Optional, Any
import uuid
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.task import TaskStatus
from app.config.database import get_db
from app.config.cache import get_redis_client


class TaskService:
    """任务管理服务，用于处理异步任务的状态跟踪和管理"""
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def create_task(self, task_type: str) -> Dict[str, Any]:
        """
        创建一个新任务并返回任务ID
        
        Args:
            task_type: 任务类型 (如 'data_processing', 'report_generation', 'ai_analysis')
            
        Returns:
            包含任务ID和状态的字典
        """
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        task = TaskStatus(
            task_id=task_id,
            task_type=task_type,
            status="pending",
            progress=0,
            started_at=datetime.now()
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        return {
            "task_id": task_id,
            "status": "pending",
            "task_type": task_type,
            "created_at": task.created_at
        }
    
    def update_task_status(
        self, 
        task_id: str, 
        status: str, 
        progress: int = None, 
        result_data: Dict = None, 
        error_message: str = None
    ) -> Dict[str, Any]:
        """
        更新任务状态
        
        Args:
            task_id: 任务ID
            status: 任务状态 ('pending', 'processing', 'completed', 'failed')
            progress: 进度百分比 (0-100)
            result_data: 任务结果数据
            error_message: 错误信息
            
        Returns:
            更新后的任务信息
        """
        task = self.db.query(TaskStatus).filter(TaskStatus.task_id == task_id).first()
        
        if not task:
            raise ValueError(f"任务ID {task_id} 不存在")
        
        # 更新任务状态
        task.status = status
        
        if progress is not None:
            task.progress = progress
            
        if result_data is not None:
            task.result_data = result_data
            
        if error_message is not None:
            task.error_message = error_message
            
        # 如果任务完成或失败，设置完成时间
        if status in ["completed", "failed"]:
            task.completed_at = datetime.now()
        
        self.db.commit()
        self.db.refresh(task)
        
        # 同时更新Redis缓存，用于快速状态查询
        redis_client = get_redis_client()
        cache_key = f"task:{task_id}:status"
        cache_data = {
            "status": status,
            "progress": task.progress,
            "updated_at": datetime.now().isoformat()
        }
        redis_client.set(cache_key, str(cache_data), ex=3600)  # 缓存1小时
        
        return {
            "task_id": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "result_data": task.result_data,
            "error_message": task.error_message,
            "started_at": task.started_at,
            "completed_at": task.completed_at
        }
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态信息
        """
        # 首先尝试从Redis缓存获取
        redis_client = get_redis_client()
        cache_key = f"task:{task_id}:status"
        cached_data = redis_client.get(cache_key)
        
        if cached_data:
            # 如果缓存中有数据，但不是completed或failed状态，则从数据库获取最新状态
            import ast
            cached_status = ast.literal_eval(cached_data.decode('utf-8'))
            if cached_status["status"] not in ["completed", "failed"]:
                # 从数据库获取最新状态
                pass
            else:
                # 使用缓存数据
                return cached_status
        
        # 从数据库获取
        task = self.db.query(TaskStatus).filter(TaskStatus.task_id == task_id).first()
        
        if not task:
            raise ValueError(f"任务ID {task_id} 不存在")
        
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "status": task.status,
            "progress": task.progress,
            "result_data": task.result_data,
            "error_message": task.error_message,
            "started_at": task.started_at,
            "completed_at": task.completed_at,
            "created_at": task.created_at
        }
    
    def list_tasks(
        self, 
        task_type: Optional[str] = None, 
        status: Optional[str] = None,
        limit: int = 10, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        列出任务
        
        Args:
            task_type: 可选，按任务类型过滤
            status: 可选，按状态过滤
            limit: 返回结果数量限制
            offset: 结果偏移量
            
        Returns:
            任务列表
        """
        query = self.db.query(TaskStatus)
        
        if task_type:
            query = query.filter(TaskStatus.task_type == task_type)
            
        if status:
            query = query.filter(TaskStatus.status == status)
            
        # 按创建时间倒序排列
        query = query.order_by(desc(TaskStatus.created_at))
        
        # 分页
        tasks = query.limit(limit).offset(offset).all()
        
        return [
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "status": task.status,
                "progress": task.progress,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "created_at": task.created_at
            }
            for task in tasks
        ]
    
    def retry_failed_task(self, task_id: str) -> Dict[str, Any]:
        """
        重试失败的任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            更新后的任务信息
        """
        task = self.db.query(TaskStatus).filter(TaskStatus.task_id == task_id).first()
        
        if not task:
            raise ValueError(f"任务ID {task_id} 不存在")
            
        if task.status != "failed":
            raise ValueError(f"只能重试失败的任务，当前任务状态为 {task.status}")
            
        if task.retry_count >= task.max_retries:
            raise ValueError(f"任务已达到最大重试次数 {task.max_retries}")
        
        # 更新任务状态
        task.status = "pending"
        task.progress = 0
        task.error_message = None
        task.retry_count += 1
        task.started_at = datetime.now()
        task.completed_at = None
        
        self.db.commit()
        self.db.refresh(task)
        
        # 更新Redis缓存
        redis_client = get_redis_client()
        cache_key = f"task:{task_id}:status"
        cache_data = {
            "status": "pending",
            "progress": 0,
            "updated_at": datetime.now().isoformat()
        }
        redis_client.set(cache_key, str(cache_data), ex=3600)
        
        # 触发相应的Celery任务
        from app.tasks.celery_app import celery_app
        
        if task.task_type == "data_processing":
            from app.tasks.data_processing import process_data_task
            process_data_task.apply_async(args=[task_id], task_id=task_id)
        elif task.task_type == "report_generation":
            from app.tasks.report_generation import generate_report_task
            generate_report_task.apply_async(args=[task_id], task_id=task_id)
        elif task.task_type == "ai_analysis":
            from app.tasks.ai_analysis import analyze_data_task
            analyze_data_task.apply_async(args=[task_id], task_id=task_id)
        
        return {
            "task_id": task.task_id,
            "status": task.status,
            "retry_count": task.retry_count,
            "max_retries": task.max_retries
        }