from sqlalchemy import Column, String, Integer, Text, JSON, DateTime
from datetime import datetime
from ..config.database import Base

class Report(Base):
    """报告模型"""
    
    __tablename__ = "report"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 创建时间
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 更新时间
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 报告标题
    title = Column(String(300), nullable=False)
    
    # 报告类型 ('analysis', 'comparison', 'forecast')
    report_type = Column(String(50), nullable=True, index=True)
    
    # 报告内容数据
    content_data = Column(JSON, nullable=True)
    
    # AI分析洞察
    ai_insights = Column(Text, nullable=True)
    
    # 文件路径 (PDF, PPT)
    file_paths = Column(JSON, nullable=True)
    
    # 报告状态
    status = Column(String(20), default="pending", index=True)
    
    # 创建人ID
    created_by = Column(Integer, nullable=True)
    
    # 完成时间
    completed_at = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Report(id={self.id}, title='{self.title}', status='{self.status}')>"
    
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