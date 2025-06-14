from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

class TaskBase(BaseModel):
    """任务基础模型"""
    task_type: str = Field(..., description="任务类型")
    
class TaskCreate(TaskBase):
    """任务创建模型"""
    params: Dict[str, Any] = Field({}, description="任务参数")
    
class TaskUpdate(BaseModel):
    """任务更新模型"""
    status: Optional[str] = Field(None, description="任务状态")
    progress: Optional[int] = Field(None, description="任务进度")
    result_data: Optional[Dict[str, Any]] = Field(None, description="任务结果数据")
    error_message: Optional[str] = Field(None, description="错误信息")
    
class TaskInDB(TaskBase):
    """数据库中的任务模型"""
    id: int = Field(..., description="任务ID")
    task_id: str = Field(..., description="Celery任务ID")
    status: str = Field(..., description="任务状态")
    progress: int = Field(..., description="任务进度")
    result_data: Optional[Dict[str, Any]] = Field(None, description="任务结果数据")
    error_message: Optional[str] = Field(None, description="错误信息")
    retry_count: int = Field(0, description="重试次数")
    max_retries: int = Field(3, description="最大重试次数")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间") 