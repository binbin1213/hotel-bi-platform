import logging
import json
import httpx
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from .celery_app import celery_app
from ..config.database import SessionLocal, get_db
from ..config.settings import settings
from ..models import HotelData, KPIMetric, Report
from ..utils.exceptions import AIServiceError
from ..services.ai_service import AIService
from ..services.task_service import TaskService

# 配置日志
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="generate_ai_analysis")
def generate_ai_analysis(self, report_id: int, task_id: str = None):
    """生成AI分析报告
    
    Args:
        report_id: 报告ID
        task_id: 任务ID（可选）
    
    Returns:
        Dict: 包含任务状态和结果的字典
    """
    logger.info(f"开始生成AI分析报告: {report_id}")
    
    # 更新任务状态
    self.update_state(state="PROCESSING", meta={"progress": 10})
    
    try:
        # 获取数据库会话
        db = SessionLocal()
        try:
            # 获取报告
            report = db.query(Report).filter(Report.id == report_id).first()
            if not report:
                raise ValueError(f"未找到报告ID: {report_id}")
            
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 20})
            
            # 获取报告相关数据
            content_data = report.content_data or {}
            hotel_ids = content_data.get("hotel_ids", [])
            date_range = content_data.get("date_range", {})
            analysis_type = content_data.get("analysis_type", "comprehensive")
            
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 40})
            
            # 使用AI服务生成分析
            ai_service = AIService(db)
            ai_response = ai_service.generate_analysis(
                hotel_ids=hotel_ids,
                date_range=date_range,
                analysis_type=analysis_type
            )
            
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 80})
            
            # 更新报告
            report.ai_insights = ai_response
            report.updated_at = datetime.utcnow()
            db.commit()
            
            # 如果有任务ID，更新任务状态
            if task_id:
                task_service = TaskService(db)
                task_service.update_task_status(
                    task_id=task_id,
                    status="completed",
                    progress=100,
                    result_data={
                        "report_id": report_id,
                        "analysis_type": analysis_type
                    }
                )
            
            # 任务完成
            return {
                "success": True,
                "message": "AI分析生成成功",
                "report_id": report_id
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"生成AI分析报告失败: {str(e)}")
        
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
        
        raise