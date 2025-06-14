from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class FileUploadRequest(BaseModel):
    """文件上传请求"""
    file_type: str = Field(..., description="文件类型，如'excel', 'csv'等")
    overwrite: bool = Field(False, description="是否覆盖现有数据")
    
    @validator('file_type')
    def validate_file_type(cls, v):
        allowed_types = ['excel', 'csv', 'json']
        if v.lower() not in allowed_types:
            raise ValueError(f"不支持的文件类型，允许的类型: {', '.join(allowed_types)}")
        return v.lower()

class DateRangeRequest(BaseModel):
    """日期范围请求"""
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v < values['start_date']:
            raise ValueError("结束日期不能早于开始日期")
        return v

class KPICalculationRequest(BaseModel):
    """KPI计算请求"""
    hotel_id: int = Field(..., description="酒店ID")
    metrics: List[str] = Field(..., description="要计算的指标列表")
    date_range: DateRangeRequest = Field(..., description="日期范围")
    
    @validator('metrics')
    def validate_metrics(cls, v):
        allowed_metrics = ['occupancy_rate', 'adr', 'revpar', 'revenue']
        for metric in v:
            if metric not in allowed_metrics:
                raise ValueError(f"不支持的指标: {metric}，允许的指标: {', '.join(allowed_metrics)}")
        return v

class ReportGenerationRequest(BaseModel):
    """报告生成请求"""
    title: str = Field(..., description="报告标题")
    report_type: str = Field(..., description="报告类型，如'analysis', 'comparison', 'forecast'")
    hotel_ids: List[int] = Field(..., description="酒店ID列表")
    date_range: DateRangeRequest = Field(..., description="日期范围")
    include_ai_analysis: bool = Field(True, description="是否包含AI分析")
    output_formats: List[str] = Field(["pdf", "ppt"], description="输出格式")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        allowed_types = ['analysis', 'comparison', 'forecast']
        if v not in allowed_types:
            raise ValueError(f"不支持的报告类型，允许的类型: {', '.join(allowed_types)}")
        return v
    
    @validator('output_formats')
    def validate_output_formats(cls, v):
        allowed_formats = ['pdf', 'ppt']
        for fmt in v:
            if fmt not in allowed_formats:
                raise ValueError(f"不支持的输出格式: {fmt}，允许的格式: {', '.join(allowed_formats)}")
        return v

class ReportCreate(BaseModel):
    """创建报告请求"""
    title: str = Field(..., description="报告标题")
    report_type: str = Field(..., description="报告类型")
    date_range: DateRangeRequest = Field(..., description="日期范围")
    hotel_ids: List[int] = Field(..., description="酒店ID列表")
    parameters: Optional[Dict[str, Any]] = Field(None, description="额外参数")
    
    @validator('report_type')
    def validate_report_type(cls, v):
        allowed_types = ['analysis', 'comparison', 'forecast']
        if v not in allowed_types:
            raise ValueError(f"不支持的报告类型，允许的类型: {', '.join(allowed_types)}")
        return v 