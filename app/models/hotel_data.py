from sqlalchemy import Column, String, Integer, Float, Date, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..config.database import Base

class HotelData(Base):
    """酒店数据模型"""
    
    __tablename__ = "hotel_data"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 酒店名称
    hotel_name = Column(String(200), nullable=False, index=True)
    
    # 酒店位置
    location = Column(String(200), nullable=True)
    
    # 房间数量
    room_count = Column(Integer, nullable=True)
    
    # 已入住房间数量
    rooms_occupied = Column(Integer, nullable=True)
    
    # 入住率
    occupancy_rate = Column(Float, nullable=True)
    
    # 收入
    revenue = Column(Float, nullable=True)
    
    # 平均房价 (Average Daily Rate)
    adr = Column(Float, nullable=True)
    
    # 每可用房收入 (Revenue Per Available Room)
    revpar = Column(Float, nullable=True)
    
    # 记录日期
    date_recorded = Column(Date, nullable=True, index=True)
    
    # 数据来源
    data_source = Column(String(100), nullable=True)
    
    # 数据是否已验证
    is_validated = Column(Boolean, default=False)
    
    # 验证错误信息
    validation_errors = Column(JSON, nullable=True)
    
    # 创建人ID
    created_by = Column(Integer, nullable=True)
    
    # 关联的KPI指标
    kpi_metrics = relationship("KPIMetric", back_populates="hotel_data")
    
    def __repr__(self):
        return f"<HotelData(id={self.id}, hotel_name='{self.hotel_name}', date='{self.date_recorded}')>"
        
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