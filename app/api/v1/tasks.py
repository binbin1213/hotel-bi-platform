from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging
from typing import List, Optional
from app.config.database import get_db
from app.schemas import TaskStatusResponse, ErrorResponse, PaginatedResponse
from app.services.task_service import TaskService

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

@router.get(
    "/tasks",
    response_model=PaginatedResponse,
    responses={500: {"model": ErrorResponse}},
    summary="获取任务列表",
    description="分页获取任务列表"
)
async def get_tasks(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    task_type: Optional[str] = Query(None, description="任务类型过滤"),
    status: Optional[str] = Query(None, description="任务状态过滤"),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    try:
        task_service = TaskService(db)
        tasks, total = task_service.get_tasks(
            page=page,
            size=size,
            task_type=task_type,
            status=status
        )
        
        # 计算总页数
        pages = (total + size - 1) // size
        
        # 转换为响应模型
        items = [TaskStatusResponse(**task.to_dict()) for task in tasks]
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.get(
    "/tasks/{task_id}",
    response_model=TaskStatusResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="获取任务状态",
    description="根据任务ID获取任务状态"
)
async def get_task_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """获取任务状态"""
    try:
        task_service = TaskService(db)
        task = task_service.get_task_by_id(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail=f"未找到任务ID: {task_id}")
        
        return TaskStatusResponse(**task.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取任务状态失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取任务状态失败: {str(e)}")

@router.delete(
    "/tasks/{task_id}",
    response_model=dict,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="取消任务",
    description="取消正在执行的任务"
)
async def cancel_task(
    task_id: str,
    db: Session = Depends(get_db)
):
    """取消任务"""
    try:
        task_service = TaskService(db)
        success = task_service.cancel_task(task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"未找到任务ID或任务无法取消: {task_id}")
        
        return {"success": True, "message": "任务已取消"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"取消任务失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"取消任务失败: {str(e)}")
