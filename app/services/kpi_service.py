import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy import func
from sqlalchemy.orm import Session
from ..models import HotelData, KPIMetric
from ..utils.exceptions import NotFoundError, DatabaseError
from ..repositories.data_repository import DataRepository

# 配置日志
logger = logging.getLogger(__name__)

class KPIService:
    """KPI服务"""
    
    def __init__(self, db: Session):
        self.db = db
        self.data_repository = DataRepository(db)
    
    def get_dashboard_summary(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """获取仪表盘摘要
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            仪表盘摘要数据
        """
        try:
            # 转换日期格式
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
            
            # 使用数据仓库获取收入指标
            if start_date_dt and end_date_dt:
                revenue_metrics = self.data_repository.calculate_revenue_metrics(
                    start_date=start_date_dt,
                    end_date=end_date_dt
                )
                
                # 使用数据仓库获取入住率
                occupancy_data = self.data_repository.calculate_occupancy_rate(
                    start_date=start_date_dt,
                    end_date=end_date_dt
                )
            else:
                # 如果没有提供日期范围，返回空摘要
                return {
                    "kpi_summary": {
                        "current": {
                            "occupancy_rate": 0,
                            "adr": 0,
                            "revpar": 0,
                            "revenue": 0
                        }
                    },
                    "hotel_count": 0,
                    "date_range": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            
            # 如果没有数据，返回空摘要
            if not revenue_metrics:
                return {
                    "kpi_summary": {
                        "current": {
                            "occupancy_rate": 0,
                            "adr": 0,
                            "revpar": 0,
                            "revenue": 0
                        }
                    },
                    "hotel_count": 0,
                    "date_range": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            
            # 计算当前周期KPI
            total_revenue = sum(item["revenue"] for item in revenue_metrics)
            avg_adr = sum(item["adr"] for item in revenue_metrics) / len(revenue_metrics) if revenue_metrics else 0
            avg_revpar = sum(item["revpar"] for item in revenue_metrics) / len(revenue_metrics) if revenue_metrics else 0
            avg_occupancy = sum(item["occupancy_rate"] for item in occupancy_data) / len(occupancy_data) if occupancy_data else 0
            
            current_kpis = {
                "occupancy_rate": avg_occupancy,
                "adr": avg_adr,
                "revpar": avg_revpar,
                "revenue": total_revenue
            }
            
            # 计算上一周期数据
            prev_kpis = {}
            changes = {}
            
            if start_date_dt and end_date_dt:
                days_diff = (end_date_dt - start_date_dt).days + 1
                
                prev_end_date = start_date_dt - timedelta(days=1)
                prev_start_date = prev_end_date - timedelta(days=days_diff-1)
                
                # 使用数据仓库获取上一周期数据
                prev_revenue_metrics = self.data_repository.calculate_revenue_metrics(
                    start_date=prev_start_date,
                    end_date=prev_end_date
                )
                
                prev_occupancy_data = self.data_repository.calculate_occupancy_rate(
                    start_date=prev_start_date,
                    end_date=prev_end_date
                )
                
                if prev_revenue_metrics:
                    prev_total_revenue = sum(item["revenue"] for item in prev_revenue_metrics)
                    prev_avg_adr = sum(item["adr"] for item in prev_revenue_metrics) / len(prev_revenue_metrics) if prev_revenue_metrics else 0
                    prev_avg_revpar = sum(item["revpar"] for item in prev_revenue_metrics) / len(prev_revenue_metrics) if prev_revenue_metrics else 0
                    prev_avg_occupancy = sum(item["occupancy_rate"] for item in prev_occupancy_data) / len(prev_occupancy_data) if prev_occupancy_data else 0
                    
                    prev_kpis = {
                        "occupancy_rate": prev_avg_occupancy,
                        "adr": prev_avg_adr,
                        "revpar": prev_avg_revpar,
                        "revenue": prev_total_revenue
                    }
                    
                    # 计算同比变化
                    for key in current_kpis:
                        if key in prev_kpis and prev_kpis[key] and prev_kpis[key] != 0:
                            changes[key] = ((current_kpis[key] - prev_kpis[key]) / prev_kpis[key]) * 100
                        else:
                            changes[key] = 0
            
            # 获取酒店数量
            hotels_query = self.db.query(HotelData.hotel_name).distinct()
            if start_date_dt:
                hotels_query = hotels_query.filter(HotelData.date_recorded >= start_date_dt)
            if end_date_dt:
                hotels_query = hotels_query.filter(HotelData.date_recorded <= end_date_dt)
            hotel_count = hotels_query.count()
            
            # 构建摘要
            summary = {
                "kpi_summary": {
                    "current": current_kpis,
                    "previous": prev_kpis,
                    "changes": changes
                },
                "hotel_count": hotel_count,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"获取仪表盘摘要失败: {str(e)}")
            raise DatabaseError(f"获取仪表盘摘要失败: {str(e)}")
    
    def get_trends(self, metrics: List[str], period: str, start_date: Optional[str] = None, end_date: Optional[str] = None) -> Dict[str, Any]:
        """获取趋势数据
        
        Args:
            metrics: 指标列表
            period: 周期类型（daily, weekly, monthly）
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            趋势数据
        """
        try:
            # 验证指标
            valid_metrics = ["occupancy_rate", "adr", "revpar", "revenue"]
            metrics = [m for m in metrics if m in valid_metrics]
            
            if not metrics:
                raise ValueError("未提供有效的指标")
            
            # 转换日期格式
            start_date_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
            end_date_dt = datetime.strptime(end_date, "%Y-%m-%d") if end_date else None
            
            # 如果没有提供日期范围，返回空趋势
            if not start_date_dt or not end_date_dt:
                return {
                    "trends": {metric: [] for metric in metrics},
                    "period": period,
                    "date_range": {
                        "start_date": start_date,
                        "end_date": end_date
                    }
                }
            
            # 将period转换为group_by参数
            group_by = "day"
            if period == "weekly":
                group_by = "week"
            elif period == "monthly":
                group_by = "month"
            
            # 使用数据仓库获取趋势数据
            trends = {metric: [] for metric in metrics}
            
            for metric in metrics:
                if metric in ["occupancy_rate", "adr", "revpar", "revenue"]:
                    # 使用数据仓库的趋势分析方法
                    trend_data = self.data_repository.get_trend_analysis(
                        start_date=start_date_dt,
                        end_date=end_date_dt,
                        metric=metric,
                        group_by=group_by
                    )
                    
                    # 格式化结果
                    trends[metric] = [
                        {
                            "period": item["date"],
                            "value": round(item["value"], 2) if item["value"] is not None else 0
                        }
                        for item in trend_data["trend_data"]
                    ]
            
            # 构建趋势数据
            result = {
                "trends": trends,
                "period": period,
                "date_range": {
                    "start_date": start_date,
                    "end_date": end_date
                }
            }
            
            return result
            
        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"获取趋势数据失败: {str(e)}")
            raise DatabaseError(f"获取趋势数据失败: {str(e)}")
    
    def get_comparison(
        self,
        metric: str,
        current_start: str,
        current_end: str,
        previous_start: str,
        previous_end: str
    ) -> Dict[str, Any]:
        """获取对比数据
        
        Args:
            metric: 指标
            current_start: 当前周期开始日期
            current_end: 当前周期结束日期
            previous_start: 上一周期开始日期
            previous_end: 上一周期结束日期
            
        Returns:
            对比数据
        """
        try:
            # 验证指标
            valid_metrics = ["occupancy_rate", "adr", "revpar", "revenue"]
            if metric not in valid_metrics:
                raise ValueError(f"无效的指标: {metric}")
            
            # 转换日期格式
            current_start_dt = datetime.strptime(current_start, "%Y-%m-%d") if current_start else None
            current_end_dt = datetime.strptime(current_end, "%Y-%m-%d") if current_end else None
            previous_start_dt = datetime.strptime(previous_start, "%Y-%m-%d") if previous_start else None
            previous_end_dt = datetime.strptime(previous_end, "%Y-%m-%d") if previous_end else None
            
            # 使用数据仓库获取当前周期数据
            if metric == "occupancy_rate":
                current_data = self.data_repository.calculate_occupancy_rate(
                    start_date=current_start_dt,
                    end_date=current_end_dt
                )
                previous_data = self.data_repository.calculate_occupancy_rate(
                    start_date=previous_start_dt,
                    end_date=previous_end_dt
                )
                
                # 计算平均值
                current_value = sum(item["occupancy_rate"] for item in current_data) / len(current_data) if current_data else 0
                previous_value = sum(item["occupancy_rate"] for item in previous_data) / len(previous_data) if previous_data else 0
            else:
                # 对于其他指标，使用revenue_metrics
                current_metrics = self.data_repository.calculate_revenue_metrics(
                    start_date=current_start_dt,
                    end_date=current_end_dt
                )
                previous_metrics = self.data_repository.calculate_revenue_metrics(
                    start_date=previous_start_dt,
                    end_date=previous_end_dt
                )
                
                if metric == "revenue":
                    # 计算总收入
                    current_value = sum(item["revenue"] for item in current_metrics) if current_metrics else 0
                    previous_value = sum(item["revenue"] for item in previous_metrics) if previous_metrics else 0
                elif metric == "adr":
                    # 计算平均ADR
                    current_value = sum(item["adr"] for item in current_metrics) / len(current_metrics) if current_metrics else 0
                    previous_value = sum(item["adr"] for item in previous_metrics) / len(previous_metrics) if previous_metrics else 0
                elif metric == "revpar":
                    # 计算平均RevPAR
                    current_value = sum(item["revpar"] for item in current_metrics) / len(current_metrics) if current_metrics else 0
                    previous_value = sum(item["revpar"] for item in previous_metrics) / len(previous_metrics) if previous_metrics else 0
            
            # 计算变化率
            if previous_value and previous_value != 0:
                change_rate = ((current_value - previous_value) / previous_value) * 100
            else:
                change_rate = 0
            
            # 获取酒店数量
            current_hotels_query = self.db.query(HotelData.hotel_name).distinct().filter(
                HotelData.date_recorded >= current_start_dt,
                HotelData.date_recorded <= current_end_dt
            )
            current_hotel_count = current_hotels_query.count()
            
            previous_hotels_query = self.db.query(HotelData.hotel_name).distinct().filter(
                HotelData.date_recorded >= previous_start_dt,
                HotelData.date_recorded <= previous_end_dt
            )
            previous_hotel_count = previous_hotels_query.count()
            
            # 构建对比数据
            result = {
                "metric": metric,
                "current": {
                    "value": round(current_value, 2) if current_value is not None else 0,
                    "date_range": {
                        "start_date": current_start,
                        "end_date": current_end
                    },
                    "hotel_count": current_hotel_count
                },
                "previous": {
                    "value": round(previous_value, 2) if previous_value is not None else 0,
                    "date_range": {
                        "start_date": previous_start,
                        "end_date": previous_end
                    },
                    "hotel_count": previous_hotel_count
                },
                "change_rate": round(change_rate, 2) if change_rate is not None else 0
            }
            
            return result
            
        except ValueError as e:
            raise
        except Exception as e:
            logger.error(f"获取对比数据失败: {str(e)}")
            raise DatabaseError(f"获取对比数据失败: {str(e)}")
