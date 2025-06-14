from sqlalchemy import Column, String, Integer, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..config.database import Base

class KPIMetric(Base):
    """KPI指标模型"""
    
    __tablename__ = "kpi_metric"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关联的酒店数据ID
    hotel_id = Column(Integer, ForeignKey("hotel_data.id"), nullable=False, index=True)
    
    # 指标名称
    metric_name = Column(String(100), nullable=False)
    
    # 指标值
    metric_value = Column(Float, nullable=True)
    
    # 指标类型 ('revenue', 'occupancy', 'satisfaction')
    metric_type = Column(String(50), nullable=True, index=True)
    
    # 周期类型 ('daily', 'weekly', 'monthly', 'yearly')
    period_type = Column(String(20), nullable=True)
    
    # 周期开始日期
    period_start = Column(Date, nullable=True)
    
    # 周期结束日期
    period_end = Column(Date, nullable=True)
    
    # 关联的酒店数据
    hotel_data = relationship("HotelData", back_populates="kpi_metrics")
    
    def __repr__(self):
        return f"<KPIMetric(id={self.id}, name='{self.metric_name}', value={self.metric_value})>"
        
    # 通用方法
    def to_dict(self):
        """将模型转换为字典"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        return result 