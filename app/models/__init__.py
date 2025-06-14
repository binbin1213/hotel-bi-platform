from .hotel_data import HotelData
from .kpi import KPIMetric
from .report import Report
from .task import TaskStatus
from ..config.database import Base

# 导出所有模型
__all__ = [
    "Base",
    "HotelData",
    "KPIMetric",
    "Report",
    "TaskStatus"
] 