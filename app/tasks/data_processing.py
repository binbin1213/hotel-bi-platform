import pandas as pd
import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from .celery_app import celery_app
from ..config.database import SessionLocal, get_db
from ..models import HotelData, KPIMetric
from ..utils.exceptions import ValidationError, FileError
from ..services.task_service import TaskService
from ..repositories.data_repository import DataRepository

# 配置日志
logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="process_excel_data")
def process_excel_data(self, file_path: str, overwrite: bool = False, task_id: Optional[str] = None) -> Dict[str, Any]:
    """处理Excel数据文件
    
    Args:
        file_path: Excel文件路径
        overwrite: 是否覆盖已存在的数据
        task_id: 任务ID（可选）
    
    Returns:
        Dict: 包含任务状态和结果的字典
    """
    logger.info(f"开始处理Excel文件: {file_path}")
    
    # 更新任务状态
    self.update_state(state="PROCESSING", meta={"progress": 10})
    
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileError(f"文件不存在: {file_path}")
        
        # 获取数据库会话
        db = SessionLocal()
        try:
            # 读取Excel文件
            if file_path.lower().endswith('.csv'):
                df = pd.read_csv(file_path)
                logger.info("读取CSV文件成功")
            else:
                df = pd.read_excel(file_path)
                logger.info("读取Excel文件成功")
            
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 30})
            
            # 验证数据
            validate_hotel_data(df)
            
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 50})
            
            # 创建数据仓库
            data_repo = DataRepository(db)
            
            # 处理数据并存储到数据库
            results = data_repo.store_hotel_data(df, overwrite)
            
            # 更新任务状态
            self.update_state(state="PROCESSING", meta={"progress": 80})
            
            # 计算KPI指标
            kpi_results = data_repo.calculate_hotel_kpis(results["hotel_ids"])
            
            # 如果有任务ID，更新任务状态
            if task_id:
                task_service = TaskService(db)
                task_service.update_task_status(
                    task_id=task_id,
                    status="completed",
                    progress=100,
                    result_data={
                        "hotel_count": len(results["hotel_ids"]),
                        "kpi_count": len(kpi_results),
                        "file_path": file_path
                    }
                )
            
            # 任务完成
            return {
                "success": True,
                "message": "数据处理成功",
                "hotel_count": len(results["hotel_ids"]),
                "kpi_count": len(kpi_results),
                "file_path": file_path
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"处理文件失败: {str(e)}")
        
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

@celery_app.task(bind=True, name="process_csv_data")
def process_csv_data(self, file_path: str, overwrite: bool = False, task_id: Optional[str] = None) -> Dict[str, Any]:
    """处理CSV数据文件
    
    Args:
        file_path: CSV文件路径
        overwrite: 是否覆盖已存在的数据
        task_id: 任务ID（可选）
    
    Returns:
        Dict: 包含任务状态和结果的字典
    """
    logger.info(f"开始处理CSV文件: {file_path}")
    # 复用Excel处理逻辑，底层pandas可以处理CSV
    return process_excel_data(self, file_path, overwrite, task_id)

def validate_hotel_data(df: pd.DataFrame) -> bool:
    """验证酒店数据"""
    # 检查必要列
    required_columns = ["hotel_name", "date_recorded", "rooms_available", "rooms_occupied", "revenue"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        raise ValidationError(
            f"缺少必要列: {', '.join(missing_columns)}",
            details={"missing_columns": missing_columns}
        )
    
    # 检查数据类型
    try:
        df["date_recorded"] = pd.to_datetime(df["date_recorded"])
    except Exception:
        raise ValidationError("日期格式无效", details={"column": "date_recorded"})
    
    # 检查数值列
    numeric_columns = ["rooms_available", "rooms_occupied", "revenue"]
    for col in numeric_columns:
        try:
            df[col] = pd.to_numeric(df[col])
        except Exception:
            raise ValidationError(f"数值格式无效", details={"column": col})
    
    # 业务规则验证
    if (df["rooms_occupied"] > df["rooms_available"]).any():
        raise ValidationError("入住房间数不能大于可用房间数", details={"rule": "rooms_occupied <= rooms_available"})
    
    if (df["revenue"] < 0).any():
        raise ValidationError("收入不能为负数", details={"rule": "revenue >= 0"})
    
    return True 