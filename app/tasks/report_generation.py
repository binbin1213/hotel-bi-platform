import logging
from .celery_app import celery_app
from ..config.database import SessionLocal, get_db
from ..services.report_service import ReportService
from ..services.task_service import TaskService
from typing import Dict, Any, Optional

# 配置日志
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="generate_pdf_report")
def generate_pdf_report(self, report_id: int, task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    生成PDF格式的报告
    
    Args:
        report_id: 报告ID
        task_id: 任务ID（可选）
    
    Returns:
        Dict: 包含任务状态和结果的字典
    """
    logger.info(f"开始生成PDF报告: {report_id}")
    
    # 更新任务状态
    self.update_state(state="PROCESSING", meta={"progress": 10})
    
    try:
        # 获取数据库会话
        db = SessionLocal()
        try:
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 30})
            
            # 创建报告服务
            report_service = ReportService(db)
            
            # 生成PDF报告
            pdf_url = report_service.generate_pdf_report(report_id)
            
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 90})
            
            # 如果有任务ID，更新任务状态
            if task_id:
                task_service = TaskService(db)
                task_service.update_task_status(
                    task_id=task_id,
                    status="completed",
                    progress=100,
                    result_data={
                        "report_id": report_id,
                        "pdf_url": pdf_url
                    }
                )
            
            return {
                "status": "success",
                "result": {
                    "report_id": report_id,
                    "pdf_url": pdf_url
                }
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"生成PDF报告失败: {str(e)}")
        
        # 如果有任务ID，更新任务状态为失败
        if task_id:
            try:
                db = next(get_db())
                task_service = TaskService(db)
                task_service.update_task_status(
                    task_id=task_id,
                    status="failed",
                    error_message=str(e)
                )
            except Exception as task_error:
                logger.error(f"更新任务状态失败: {str(task_error)}")
        
        return {
            "status": "error",
            "error": str(e)
        }

@celery_app.task(bind=True, name="generate_ppt_report")
def generate_ppt_report(self, report_id: int, task_id: Optional[str] = None) -> Dict[str, Any]:
    """
    生成PPT格式的报告
    
    Args:
        report_id: 报告ID
        task_id: 任务ID（可选）
    
    Returns:
        Dict: 包含任务状态和结果的字典
    """
    logger.info(f"开始生成PPT报告: {report_id}")
    
    # 更新任务状态
    self.update_state(state="PROCESSING", meta={"progress": 10})
    
    try:
        # 获取数据库会话
        db = SessionLocal()
        try:
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 30})
            
            # 创建报告服务
            report_service = ReportService(db)
            
            # 生成PPT报告
            ppt_url = report_service.generate_ppt_report(report_id)
            
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 90})
            
            # 如果有任务ID，更新任务状态
            if task_id:
                task_service = TaskService(db)
                task_service.update_task_status(
                    task_id=task_id,
                    status="completed",
                    progress=100,
                    result_data={
                        "report_id": report_id,
                        "ppt_url": ppt_url
                    }
                )
            
            return {
                "status": "success",
                "result": {
                    "report_id": report_id,
                    "ppt_url": ppt_url
                }
            }
        finally:
            db.close()
    except Exception as e:
        logger.error(f"生成PPT报告失败: {str(e)}")
        
        # 如果有任务ID，更新任务状态为失败
        if task_id:
            try:
                db = next(get_db())
                task_service = TaskService(db)
                task_service.update_task_status(
                    task_id=task_id,
                    status="failed",
                    error_message=str(e)
                )
            except Exception as task_error:
                logger.error(f"更新任务状态失败: {str(task_error)}")
        
        return {
            "status": "error",
            "error": str(e)
        } 