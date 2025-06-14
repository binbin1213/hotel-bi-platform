from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="操作是否成功")
    message: Optional[str] = Field(None, description="响应消息")

class ErrorResponse(BaseResponse):
    """错误响应模型"""
    success: bool = Field(False, description="操作失败")
    error: str = Field(..., description="错误信息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")

class FileUploadResponse(BaseResponse):
    """文件上传响应"""
    file_id: str = Field(..., description="文件ID")
    file_name: str = Field(..., description="文件名")
    task_id: Optional[str] = Field(None, description="处理任务ID")
    
class HotelDataResponse(BaseModel):
    """酒店数据响应"""
    id: int = Field(..., description="酒店数据ID")
    hotel_name: str = Field(..., description="酒店名称")
    location: Optional[str] = Field(None, description="酒店位置")
    room_count: Optional[int] = Field(None, description="房间数量")
    occupancy_rate: Optional[float] = Field(None, description="入住率")
    revenue: Optional[float] = Field(None, description="收入")
    adr: Optional[float] = Field(None, description="平均房价")
    revpar: Optional[float] = Field(None, description="每可用房收入")
    date_recorded: Optional[date] = Field(None, description="记录日期")
    created_at: datetime = Field(..., description="创建时间")
    
class KPIMetricResponse(BaseModel):
    """KPI指标响应"""
    id: int = Field(..., description="KPI指标ID")
    hotel_id: int = Field(..., description="酒店ID")
    metric_name: str = Field(..., description="指标名称")
    metric_value: Optional[float] = Field(None, description="指标值")
    metric_type: Optional[str] = Field(None, description="指标类型")
    period_type: Optional[str] = Field(None, description="周期类型")
    period_start: Optional[date] = Field(None, description="周期开始日期")
    period_end: Optional[date] = Field(None, description="周期结束日期")
    
class ReportResponse(BaseModel):
    """报告响应"""
    id: int = Field(..., description="报告ID")
    title: str = Field(..., description="报告标题")
    report_type: str = Field(..., description="报告类型")
    status: str = Field(..., description="报告状态")
    created_at: datetime = Field(..., description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    file_paths: Optional[Dict[str, str]] = Field(None, description="文件路径")
    
class TaskStatusResponse(BaseModel):
    """任务状态响应"""
    id: int = Field(..., description="任务ID")
    task_id: str = Field(..., description="Celery任务ID")
    task_type: str = Field(..., description="任务类型")
    status: str = Field(..., description="任务状态")
    progress: int = Field(..., description="任务进度")
    started_at: Optional[datetime] = Field(None, description="开始时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    error_message: Optional[str] = Field(None, description="错误信息")
    
class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List[Any] = Field(..., description="数据项")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页码")
    size: int = Field(..., description="每页大小")
    pages: int = Field(..., description="总页数")

class FileUrlResponse(BaseModel):
    """文件URL响应模式"""
    file_url: str
    file_type: str
    expires_in: int