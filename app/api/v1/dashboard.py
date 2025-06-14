from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging
from typing import Optional
from app.config.database import get_db
from app.config.cache import cache
from app.schemas import DateRangeRequest, ErrorResponse
from app.services.data_service import DataService
from app.services.kpi_service import KPIService

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

@router.get(
    "/dashboard/summary",
    response_model=dict,
    responses={500: {"model": ErrorResponse}},
    summary="获取仪表盘摘要",
    description="获取仪表盘摘要数据，包含关键KPI指标"
)
async def get_dashboard_summary(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """获取仪表盘摘要"""
    try:
        # 尝试从缓存获取
        cache_key = f"dashboard_summary:{start_date}:{end_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库获取
        kpi_service = KPIService(db)
        summary = kpi_service.get_dashboard_summary(start_date, end_date)
        
        # 存入缓存
        cache.set(cache_key, summary, expire=3600)  # 缓存1小时
        
        return summary
        
    except Exception as e:
        logger.error(f"获取仪表盘摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取仪表盘摘要失败: {str(e)}")

@router.get(
    "/dashboard/trends",
    response_model=dict,
    responses={500: {"model": ErrorResponse}},
    summary="获取趋势数据",
    description="获取关键指标的趋势数据"
)
async def get_trends(
    metrics: str = Query("occupancy_rate,adr,revpar", description="要获取的指标，逗号分隔"),
    period: str = Query("daily", description="周期类型: daily, weekly, monthly"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """获取趋势数据"""
    try:
        # 解析指标列表
        metric_list = metrics.split(",")
        
        # 尝试从缓存获取
        cache_key = f"dashboard_trends:{metrics}:{period}:{start_date}:{end_date}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库获取
        kpi_service = KPIService(db)
        trends = kpi_service.get_trends(metric_list, period, start_date, end_date)
        
        # 存入缓存
        cache.set(cache_key, trends, expire=3600)  # 缓存1小时
        
        return trends
        
    except Exception as e:
        logger.error(f"获取趋势数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取趋势数据失败: {str(e)}")

@router.get(
    "/dashboard/comparison",
    response_model=dict,
    responses={500: {"model": ErrorResponse}},
    summary="获取对比数据",
    description="获取不同时期的数据对比"
)
async def get_comparison(
    metric: str = Query("occupancy_rate", description="要对比的指标"),
    current_start: str = Query(..., description="当前周期开始日期 (YYYY-MM-DD)"),
    current_end: str = Query(..., description="当前周期结束日期 (YYYY-MM-DD)"),
    previous_start: str = Query(..., description="上一周期开始日期 (YYYY-MM-DD)"),
    previous_end: str = Query(..., description="上一周期结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """获取对比数据"""
    try:
        # 尝试从缓存获取
        cache_key = f"dashboard_comparison:{metric}:{current_start}:{current_end}:{previous_start}:{previous_end}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return cached_data
        
        # 从数据库获取
        kpi_service = KPIService(db)
        comparison = kpi_service.get_comparison(
            metric,
            current_start, current_end,
            previous_start, previous_end
        )
        
        # 存入缓存
        cache.set(cache_key, comparison, expire=3600)  # 缓存1小时
        
        return comparison
        
    except Exception as e:
        logger.error(f"获取对比数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取对比数据失败: {str(e)}")
