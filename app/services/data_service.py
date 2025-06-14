import logging
from datetime import datetime
from typing import Tuple, List, Optional, Dict, Any
from fastapi import BackgroundTasks
from sqlalchemy import func, desc
from sqlalchemy.orm import Session
from ..models import HotelData, TaskStatus
from ..utils.exceptions import ValidationError, NotFoundError, DatabaseError
from ..tasks.data_processing import process_excel_data, process_excel_data as process_csv_data

# 配置日志
logger = logging.getLogger(__name__)

class DataService:
    """数据服务"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def process_file_async(self, background_tasks: BackgroundTasks, file_path: str, file_type: str, overwrite: bool = False) -> str:
        """异步处理文件
        
        Args:
            background_tasks: 后台任务对象
            file_path: 文件路径
            file_type: 文件类型
            overwrite: 是否覆盖现有数据
            
        Returns:
            任务ID
        """
        try:
            # 创建任务记录
            task = TaskStatus(
                task_id=f"process_file_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                task_type="file_processing",
                status="pending",
                progress=0,
                result_data={
                    "file_path": file_path,
                    "file_type": file_type,
                    "overwrite": overwrite
                }
            )
            self.db.add(task)
            self.db.commit()
            
            # 添加后台任务
            if file_type == "excel":
                # 使用Celery任务处理Excel
                process_excel_data.delay(file_path, overwrite)
            elif file_type == "csv":
                # 处理CSV文件（复用Excel处理逻辑，底层pandas可以处理CSV）
                process_csv_data.delay(file_path, overwrite)
            else:
                raise ValidationError(f"不支持的文件类型: {file_type}")
            
            return task.task_id
            
        except Exception as e:
            logger.error(f"创建文件处理任务失败: {str(e)}")
            raise DatabaseError(f"创建文件处理任务失败: {str(e)}")
    
    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """获取任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务状态对象
        """
        try:
            return self.db.query(TaskStatus).filter(TaskStatus.task_id == task_id).first()
        except Exception as e:
            logger.error(f"获取任务状态失败: {str(e)}")
            raise DatabaseError(f"获取任务状态失败: {str(e)}")
    
    def get_hotels(
        self,
        page: int = 1,
        size: int = 10,
        hotel_name: Optional[str] = None,
        location: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[HotelData], int]:
        """获取酒店数据列表
        
        Args:
            page: 页码
            size: 每页大小
            hotel_name: 酒店名称过滤
            location: 位置过滤
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            酒店数据列表和总数
        """
        try:
            # 构建查询
            query = self.db.query(HotelData)
            
            # 应用过滤条件
            if hotel_name:
                query = query.filter(HotelData.hotel_name.ilike(f"%{hotel_name}%"))
            
            if location:
                query = query.filter(HotelData.location.ilike(f"%{location}%"))
            
            if start_date:
                query = query.filter(HotelData.date_recorded >= start_date)
            
            if end_date:
                query = query.filter(HotelData.date_recorded <= end_date)
            
            # 计算总数
            total = query.count()
            
            # 应用分页
            query = query.order_by(desc(HotelData.date_recorded))
            query = query.offset((page - 1) * size).limit(size)
            
            # 执行查询
            hotels = query.all()
            
            return hotels, total
            
        except Exception as e:
            logger.error(f"获取酒店数据失败: {str(e)}")
            raise DatabaseError(f"获取酒店数据失败: {str(e)}")
    
    def get_hotel_by_id(self, hotel_id: int) -> Optional[HotelData]:
        """根据ID获取酒店数据
        
        Args:
            hotel_id: 酒店ID
            
        Returns:
            酒店数据对象
        """
        try:
            hotel = self.db.query(HotelData).filter(HotelData.id == hotel_id).first()
            
            if not hotel:
                raise NotFoundError(f"未找到酒店ID: {hotel_id}", "hotel", hotel_id)
            
            return hotel
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"获取酒店数据失败: {str(e)}")
            raise DatabaseError(f"获取酒店数据失败: {str(e)}")
    
    def get_data_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """获取数据摘要
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            数据摘要
        """
        try:
            # 构建查询
            query = self.db.query(HotelData)
            
            # 应用日期过滤
            if start_date:
                query = query.filter(HotelData.date_recorded >= start_date)
            
            if end_date:
                query = query.filter(HotelData.date_recorded <= end_date)
            
            # 计算统计数据
            hotel_count = query.distinct(HotelData.hotel_name).count()
            total_records = query.count()
            
            # 计算平均指标
            avg_occupancy = self.db.query(func.avg(HotelData.occupancy_rate)).filter(HotelData.occupancy_rate.isnot(None)).scalar() or 0
            avg_adr = self.db.query(func.avg(HotelData.adr)).filter(HotelData.adr.isnot(None)).scalar() or 0
            avg_revpar = self.db.query(func.avg(HotelData.revpar)).filter(HotelData.revpar.isnot(None)).scalar() or 0
            total_revenue = self.db.query(func.sum(HotelData.revenue)).filter(HotelData.revenue.isnot(None)).scalar() or 0
            
            # 获取日期范围
            min_date = self.db.query(func.min(HotelData.date_recorded)).scalar()
            max_date = self.db.query(func.max(HotelData.date_recorded)).scalar()
            
            min_date_str = min_date.strftime("%Y-%m-%d") if min_date else None
            max_date_str = max_date.strftime("%Y-%m-%d") if max_date else None
            
            # 构建摘要
            summary = {
                "hotel_count": hotel_count,
                "total_records": total_records,
                "date_range": {
                    "min_date": min_date_str,
                    "max_date": max_date_str
                },
                "metrics": {
                    "avg_occupancy_rate": round(avg_occupancy, 2),
                    "avg_adr": round(avg_adr, 2),
                    "avg_revpar": round(avg_revpar, 2),
                    "total_revenue": round(total_revenue, 2)
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取数据摘要失败: {str(e)}")
            raise DatabaseError(f"获取数据摘要失败: {str(e)}")
