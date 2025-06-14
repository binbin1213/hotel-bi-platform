from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import logging
import pandas as pd
from sqlalchemy import func, desc, and_, or_, text
from sqlalchemy.orm import Session

from app.models.hotel_data import HotelData
from app.models.kpi import KPIMetric
from app.config.database import get_db

# 配置日志
logger = logging.getLogger(__name__)

class DataRepository:
    """
    数据仓库 - 封装所有数据库查询操作，提高查询效率
    """
    
    def __init__(self, db: Session = None):
        self.db = db or next(get_db())
    
    def get_hotel_data_by_id(self, hotel_data_id: int) -> Optional[HotelData]:
        """
        通过ID获取酒店数据
        
        Args:
            hotel_data_id: 酒店数据ID
            
        Returns:
            酒店数据对象
        """
        return self.db.query(HotelData).filter(HotelData.id == hotel_data_id).first()
    
    def store_hotel_data(self, df: pd.DataFrame, overwrite: bool = False) -> Dict[str, Any]:
        """
        处理并存储酒店数据
        
        Args:
            df: 包含酒店数据的DataFrame
            overwrite: 是否覆盖已存在的数据
            
        Returns:
            包含处理结果的字典
        """
        # 清洗数据
        df = df.dropna(subset=["hotel_name", "date_recorded"])  # 删除关键列为空的行
        df = df.drop_duplicates(subset=["hotel_name", "date_recorded"])  # 删除重复行
        
        # 计算入住率
        if "rooms_available" in df.columns and "rooms_occupied" in df.columns:
            df["occupancy_rate"] = (df["rooms_occupied"] / df["rooms_available"]) * 100
        
        # 计算ADR (Average Daily Rate)
        if "revenue" in df.columns and "rooms_occupied" in df.columns:
            df["adr"] = df["revenue"] / df["rooms_occupied"]
            # 处理分母为0的情况
            df["adr"] = df["adr"].fillna(0)
        
        # 计算RevPAR (Revenue Per Available Room)
        if "revenue" in df.columns and "rooms_available" in df.columns:
            df["revpar"] = df["revenue"] / df["rooms_available"]
            # 处理分母为0的情况
            df["revpar"] = df["revpar"].fillna(0)
        
        # 存储数据
        hotel_ids = []
        
        for _, row in df.iterrows():
            # 检查是否存在相同记录
            existing_record = self.db.query(HotelData).filter(
                HotelData.hotel_name == row["hotel_name"],
                HotelData.date_recorded == row["date_recorded"]
            ).first()
            
            if existing_record and not overwrite:
                # 如果存在且不覆盖，则跳过
                hotel_ids.append(existing_record.id)
                continue
            
            if existing_record and overwrite:
                # 如果存在且覆盖，则更新
                existing_record.room_count = row.get("rooms_available")
                existing_record.occupancy_rate = row.get("occupancy_rate")
                existing_record.revenue = row.get("revenue")
                existing_record.adr = row.get("adr")
                existing_record.revpar = row.get("revpar")
                existing_record.updated_at = datetime.utcnow()
                self.db.commit()
                hotel_ids.append(existing_record.id)
            else:
                # 如果不存在，则创建
                hotel_data = HotelData(
                    hotel_name=row["hotel_name"],
                    location=row.get("location"),
                    room_count=row.get("rooms_available"),
                    occupancy_rate=row.get("occupancy_rate"),
                    revenue=row.get("revenue"),
                    adr=row.get("adr"),
                    revpar=row.get("revpar"),
                    date_recorded=row["date_recorded"],
                    is_validated=True
                )
                self.db.add(hotel_data)
                self.db.commit()
                hotel_ids.append(hotel_data.id)
        
        return {"hotel_ids": hotel_ids}
    
    def calculate_hotel_kpis(self, hotel_ids: List[int]) -> List[int]:
        """
        计算酒店KPI指标
        
        Args:
            hotel_ids: 酒店数据ID列表
            
        Returns:
            KPI指标ID列表
        """
        kpi_ids = []
        
        for hotel_id in hotel_ids:
            # 获取酒店数据
            hotel = self.db.query(HotelData).filter(HotelData.id == hotel_id).first()
            if not hotel:
                continue
            
            # 创建KPI指标
            metrics = [
                {"name": "occupancy_rate", "value": hotel.occupancy_rate, "type": "occupancy"},
                {"name": "adr", "value": hotel.adr, "type": "revenue"},
                {"name": "revpar", "value": hotel.revpar, "type": "revenue"},
                {"name": "revenue", "value": hotel.revenue, "type": "revenue"}
            ]
            
            for metric in metrics:
                kpi = KPIMetric(
                    hotel_id=hotel_id,
                    metric_name=metric["name"],
                    metric_value=metric["value"],
                    metric_type=metric["type"],
                    period_type="daily",
                    period_start=hotel.date_recorded,
                    period_end=hotel.date_recorded
                )
                self.db.add(kpi)
                self.db.flush()
                kpi_ids.append(kpi.id)
            
            self.db.commit()
        
        return kpi_ids
    
    def get_hotel_data_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime,
        hotel_name: Optional[str] = None
    ) -> List[HotelData]:
        """
        获取指定日期范围内的酒店数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            hotel_name: 可选，酒店名称
            
        Returns:
            酒店数据列表
        """
        query = self.db.query(HotelData).filter(
            HotelData.date_recorded >= start_date,
            HotelData.date_recorded <= end_date
        )
        
        if hotel_name:
            query = query.filter(HotelData.hotel_name == hotel_name)
            
        return query.all()
    
    def get_kpi_metrics_by_hotel_data_id(self, hotel_data_id: int) -> List[KPIMetric]:
        """
        获取指定酒店数据的KPI指标
        
        Args:
            hotel_data_id: 酒店数据ID
            
        Returns:
            KPI指标列表
        """
        return self.db.query(KPIMetric).filter(KPIMetric.hotel_id == hotel_data_id).all()
    
    def calculate_occupancy_rate(
        self, 
        start_date: datetime, 
        end_date: datetime,
        hotel_name: Optional[str] = None,
        group_by: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        计算指定日期范围内的入住率
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            hotel_name: 可选，酒店名称
            group_by: 分组方式，可选值：day, week, month
            
        Returns:
            入住率数据列表，包含日期和入住率
        """
        # 根据分组方式选择日期表达式
        if group_by == "day":
            date_expr = func.date(HotelData.date_recorded)
        elif group_by == "week":
            date_expr = func.date_trunc('week', HotelData.date_recorded)
        elif group_by == "month":
            date_expr = func.date_trunc('month', HotelData.date_recorded)
        else:
            date_expr = func.date(HotelData.date_recorded)
        
        # 构建查询
        query = self.db.query(
            date_expr.label('date'),
            func.sum(HotelData.rooms_occupied).label('rooms_occupied'),
            func.sum(HotelData.rooms_available).label('rooms_available'),
            (func.sum(HotelData.rooms_occupied) / func.nullif(func.sum(HotelData.rooms_available), 0) * 100).label('occupancy_rate')
        ).filter(
            HotelData.date_recorded >= start_date,
            HotelData.date_recorded <= end_date
        ).group_by(date_expr).order_by(date_expr)
        
        # 添加酒店名称过滤
        if hotel_name:
            query = query.filter(HotelData.hotel_name == hotel_name)
        
        # 执行查询
        result = query.all()
        
        # 格式化结果
        return [
            {
                "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                "rooms_occupied": float(row.rooms_occupied) if row.rooms_occupied is not None else 0,
                "rooms_available": float(row.rooms_available) if row.rooms_available is not None else 0,
                "occupancy_rate": float(row.occupancy_rate) if row.occupancy_rate is not None else 0
            }
            for row in result
        ]
    
    def calculate_revenue_metrics(
        self, 
        start_date: datetime, 
        end_date: datetime,
        hotel_name: Optional[str] = None,
        group_by: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        计算指定日期范围内的收入指标
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            hotel_name: 可选，酒店名称
            group_by: 分组方式，可选值：day, week, month
            
        Returns:
            收入指标数据列表，包含日期、收入、ADR和RevPAR
        """
        # 根据分组方式选择日期表达式
        if group_by == "day":
            date_expr = func.date(HotelData.date_recorded)
        elif group_by == "week":
            date_expr = func.date_trunc('week', HotelData.date_recorded)
        elif group_by == "month":
            date_expr = func.date_trunc('month', HotelData.date_recorded)
        else:
            date_expr = func.date(HotelData.date_recorded)
        
        # 构建查询
        query = self.db.query(
            date_expr.label('date'),
            func.sum(HotelData.revenue).label('revenue'),
            func.sum(HotelData.rooms_occupied).label('rooms_occupied'),
            func.sum(HotelData.rooms_available).label('rooms_available'),
            (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_occupied), 0)).label('adr'),
            (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_available), 0)).label('revpar')
        ).filter(
            HotelData.date_recorded >= start_date,
            HotelData.date_recorded <= end_date
        ).group_by(date_expr).order_by(date_expr)
        
        # 添加酒店名称过滤
        if hotel_name:
            query = query.filter(HotelData.hotel_name == hotel_name)
        
        # 执行查询
        result = query.all()
        
        # 格式化结果
        return [
            {
                "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                "revenue": float(row.revenue) if row.revenue is not None else 0,
                "adr": float(row.adr) if row.adr is not None else 0,
                "revpar": float(row.revpar) if row.revpar is not None else 0,
                "rooms_occupied": float(row.rooms_occupied) if row.rooms_occupied is not None else 0,
                "rooms_available": float(row.rooms_available) if row.rooms_available is not None else 0
            }
            for row in result
        ]
    
    def get_hotel_performance_comparison(
        self,
        start_date: datetime,
        end_date: datetime,
        metrics: List[str] = ["occupancy_rate", "adr", "revpar"]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取不同酒店的性能比较数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            metrics: 要比较的指标列表
            
        Returns:
            不同酒店的性能比较数据
        """
        result = {}
        
        # 查询所有酒店
        hotels = self.db.query(HotelData.hotel_name).distinct().all()
        hotel_names = [hotel.hotel_name for hotel in hotels]
        
        # 构建查询
        for metric in metrics:
            if metric == "occupancy_rate":
                query = self.db.query(
                    HotelData.hotel_name,
                    (func.sum(HotelData.rooms_occupied) / func.nullif(func.sum(HotelData.rooms_available), 0) * 100).label('value')
                )
            elif metric == "adr":
                query = self.db.query(
                    HotelData.hotel_name,
                    (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_occupied), 0)).label('value')
                )
            elif metric == "revpar":
                query = self.db.query(
                    HotelData.hotel_name,
                    (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_available), 0)).label('value')
                )
            else:
                continue
            
            # 添加日期过滤
            query = query.filter(
                HotelData.date_recorded >= start_date,
                HotelData.date_recorded <= end_date
            ).group_by(HotelData.hotel_name).order_by(desc('value'))
            
            # 执行查询
            metric_result = query.all()
            
            # 格式化结果
            result[metric] = [
                {
                    "hotel_name": row.hotel_name,
                    "value": float(row.value) if row.value is not None else 0
                }
                for row in metric_result
            ]
        
        return result
    
    def get_trend_analysis(
        self,
        start_date: datetime,
        end_date: datetime,
        metric: str = "occupancy_rate",
        hotel_name: Optional[str] = None,
        group_by: str = "day"
    ) -> Dict[str, Any]:
        """
        获取指标趋势分析数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            metric: 指标名称
            hotel_name: 可选，酒店名称
            group_by: 分组方式，可选值：day, week, month
            
        Returns:
            趋势分析数据
        """
        # 根据分组方式选择日期表达式
        if group_by == "day":
            date_expr = func.date(HotelData.date_recorded)
        elif group_by == "week":
            date_expr = func.date_trunc('week', HotelData.date_recorded)
        elif group_by == "month":
            date_expr = func.date_trunc('month', HotelData.date_recorded)
        else:
            date_expr = func.date(HotelData.date_recorded)
        
        # 构建查询
        if metric == "occupancy_rate":
            value_expr = (func.sum(HotelData.rooms_occupied) / func.nullif(func.sum(HotelData.rooms_available), 0) * 100)
        elif metric == "adr":
            value_expr = (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_occupied), 0))
        elif metric == "revpar":
            value_expr = (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_available), 0))
        elif metric == "revenue":
            value_expr = func.sum(HotelData.revenue)
        else:
            value_expr = func.sum(HotelData.revenue)  # 默认使用收入
        
        query = self.db.query(
            date_expr.label('date'),
            value_expr.label('value')
        ).filter(
            HotelData.date_recorded >= start_date,
            HotelData.date_recorded <= end_date
        )
        
        # 添加酒店名称过滤
        if hotel_name:
            query = query.filter(HotelData.hotel_name == hotel_name)
        
        # 分组和排序
        query = query.group_by(date_expr).order_by(date_expr)
        
        # 执行查询
        result = query.all()
        
        # 计算同比和环比数据
        # 这里简化处理，仅返回原始趋势数据
        trend_data = [
            {
                "date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date),
                "value": float(row.value) if row.value is not None else 0
            }
            for row in result
        ]
        
        return {
            "metric": metric,
            "hotel_name": hotel_name,
            "group_by": group_by,
            "trend_data": trend_data
        }
    
    def get_seasonal_patterns(
        self,
        year: int,
        metric: str = "occupancy_rate",
        hotel_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取季节性模式数据
        
        Args:
            year: 年份
            metric: 指标名称
            hotel_name: 可选，酒店名称
            
        Returns:
            季节性模式数据
        """
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31)
        
        # 按月分组
        date_expr = func.date_trunc('month', HotelData.date_recorded)
        
        # 构建查询
        if metric == "occupancy_rate":
            value_expr = (func.sum(HotelData.rooms_occupied) / func.nullif(func.sum(HotelData.rooms_available), 0) * 100)
        elif metric == "adr":
            value_expr = (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_occupied), 0))
        elif metric == "revpar":
            value_expr = (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_available), 0))
        elif metric == "revenue":
            value_expr = func.sum(HotelData.revenue)
        else:
            value_expr = func.sum(HotelData.revenue)  # 默认使用收入
        
        query = self.db.query(
            func.extract('month', HotelData.date_recorded).label('month'),
            value_expr.label('value')
        ).filter(
            HotelData.date_recorded >= start_date,
            HotelData.date_recorded <= end_date
        )
        
        # 添加酒店名称过滤
        if hotel_name:
            query = query.filter(HotelData.hotel_name == hotel_name)
        
        # 分组和排序
        query = query.group_by('month').order_by('month')
        
        # 执行查询
        result = query.all()
        
        # 格式化结果
        monthly_data = [
            {
                "month": int(row.month),
                "value": float(row.value) if row.value is not None else 0
            }
            for row in result
        ]
        
        return {
            "year": year,
            "metric": metric,
            "hotel_name": hotel_name,
            "monthly_data": monthly_data
        }
    
    def get_hotel_rankings(
        self,
        start_date: datetime,
        end_date: datetime,
        metric: str = "revenue",
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取酒店排名数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            metric: 排名指标
            limit: 返回结果数量限制
            
        Returns:
            酒店排名数据
        """
        # 构建查询
        if metric == "occupancy_rate":
            value_expr = (func.sum(HotelData.rooms_occupied) / func.nullif(func.sum(HotelData.rooms_available), 0) * 100)
        elif metric == "adr":
            value_expr = (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_occupied), 0))
        elif metric == "revpar":
            value_expr = (func.sum(HotelData.revenue) / func.nullif(func.sum(HotelData.rooms_available), 0))
        elif metric == "revenue":
            value_expr = func.sum(HotelData.revenue)
        else:
            value_expr = func.sum(HotelData.revenue)  # 默认使用收入
        
        query = self.db.query(
            HotelData.hotel_name,
            value_expr.label('value')
        ).filter(
            HotelData.date_recorded >= start_date,
            HotelData.date_recorded <= end_date
        ).group_by(HotelData.hotel_name).order_by(desc('value')).limit(limit)
        
        # 执行查询
        result = query.all()
        
        # 格式化结果
        return [
            {
                "hotel_name": row.hotel_name,
                "value": float(row.value) if row.value is not None else 0
            }
            for row in result
        ]