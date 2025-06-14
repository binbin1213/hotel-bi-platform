from sqlalchemy import Column, String, Integer, Text, JSON, DateTime
from datetime import datetime
from ..config.database import Base

class TaskStatus(Base):
    """任务状态模型"""
    
    __tablename__ = "task_status"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 任务ID
    task_id = Column(String(100), unique=True, nullable=False, index=True)
    
    # 任务类型
    task_type = Column(String(50), nullable=False, index=True)
    
    # 任务状态
    status = Column(String(20), default="pending", index=True)
    
    # 任务进度
    progress = Column(Integer, default=0)
    
    # 任务结果数据
    result_data = Column(JSON, nullable=True)
    
    # 错误信息
    error_message = Column(Text, nullable=True)
    
    # 重试次数
    retry_count = Column(Integer, default=0)
    
    # 最大重试次数
    max_retries = Column(Integer, default=3)
    
    # 开始时间
    started_at = Column(DateTime, nullable=True)
    
    # 完成时间
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<TaskStatus(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"
        
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