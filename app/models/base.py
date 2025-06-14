from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
from ..config.database import Base

class BaseModel:
    """所有模型的基类（抽象基类）"""
    
    # 将类名转换为表名
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
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