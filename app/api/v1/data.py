from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import logging
from typing import List, Optional
from app.config.database import get_db
from app.schemas import HotelDataResponse, DateRangeRequest, ErrorResponse, PaginatedResponse
from app.services.data_service import DataService

# 配置日志
logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter()

@router.get(
    "/data/hotels",
    response_model=PaginatedResponse,
    responses={500: {"model": ErrorResponse}},
    summary="获取酒店数据列表",
    description="分页获取酒店数据列表"
)
async def get_hotels(
    page: int = Query(1, ge=1, description="页码"),
    size: int = Query(10, ge=1, le=100, description="每页数量"),
    hotel_name: Optional[str] = Query(None, description="酒店名称过滤"),
    location: Optional[str] = Query(None, description="位置过滤"),
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """获取酒店数据列表"""
    try:
        data_service = DataService(db)
        hotels, total = data_service.get_hotels(
            page=page,
            size=size,
            hotel_name=hotel_name,
            location=location,
            start_date=start_date,
            end_date=end_date
        )
        
        # 计算总页数
        pages = (total + size - 1) // size
        
        # 转换为响应模型
        items = [HotelDataResponse(**hotel.to_dict()) for hotel in hotels]
        
        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"获取酒店数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取酒店数据失败: {str(e)}")

@router.get(
    "/data/hotels/{hotel_id}",
    response_model=HotelDataResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    summary="获取单个酒店数据",
    description="根据ID获取单个酒店数据详情"
)
async def get_hotel(
    hotel_id: int,
    db: Session = Depends(get_db)
):
    """获取单个酒店数据"""
    try:
        data_service = DataService(db)
        hotel = data_service.get_hotel_by_id(hotel_id)
        
        if not hotel:
            raise HTTPException(status_code=404, detail=f"未找到酒店ID: {hotel_id}")
        
        return HotelDataResponse(**hotel.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取酒店数据失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取酒店数据失败: {str(e)}")

@router.get(
    "/data/summary",
    response_model=dict,
    responses={500: {"model": ErrorResponse}},
    summary="获取数据摘要",
    description="获取酒店数据的摘要统计信息"
)
async def get_data_summary(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """获取数据摘要"""
    try:
        data_service = DataService(db)
        summary = data_service.get_data_summary(start_date, end_date)
        
        return summary
        
    except Exception as e:
        logger.error(f"获取数据摘要失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取数据摘要失败: {str(e)}")