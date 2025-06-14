import logging
import json
import hashlib
import httpx
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..config.settings import settings
from ..config.cache import get_redis_client
from ..models import HotelData, KPIMetric, Report
from ..utils.exceptions import AIServiceError
from ..repositories.data_repository import DataRepository

# 配置日志
logger = logging.getLogger(__name__)

class AIService:
    """AI分析服务类，提供与AI模型交互的功能"""
    
    def __init__(self, db: Session):
        """初始化AI服务
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.redis_client = get_redis_client()
        self.cache_ttl = 3600 * 24  # 缓存有效期，默认24小时
        self.data_repository = DataRepository(db)
    
    def generate_analysis(self, hotel_ids: List[int], date_range: Dict[str, str], 
                         analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """生成AI分析
        
        Args:
            hotel_ids: 酒店ID列表
            date_range: 日期范围，包含start_date和end_date
            analysis_type: 分析类型，可选值：comprehensive, revenue, operational, competitive, forecast
            
        Returns:
            分析结果字典
        """
        try:
            # 生成缓存键
            cache_key = self._generate_cache_key(hotel_ids, date_range, analysis_type)
            
            # 尝试从缓存获取
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info(f"从缓存获取AI分析结果: {cache_key}")
                return cached_result
            
            # 获取酒店数据
            hotel_data = self._get_hotel_data(hotel_ids, date_range)
            
            # 构建AI提示词
            prompt = self._build_prompt(hotel_data, analysis_type)
            
            # 调用AI服务
            ai_response = self._call_ai_service(prompt)
            
            # 解析AI响应
            parsed_result = self._parse_ai_response(ai_response, analysis_type)
            
            # 缓存结果
            self._cache_result(cache_key, parsed_result)
            
            return parsed_result
            
        except Exception as e:
            logger.error(f"生成AI分析失败: {str(e)}")
            raise AIServiceError(f"生成AI分析失败: {str(e)}")
    
    def _generate_cache_key(self, hotel_ids: List[int], date_range: Dict[str, str], 
                           analysis_type: str) -> str:
        """生成缓存键
        
        Args:
            hotel_ids: 酒店ID列表
            date_range: 日期范围
            analysis_type: 分析类型
            
        Returns:
            缓存键字符串
        """
        # 对输入参数进行排序和序列化，确保相同参数生成相同的键
        key_data = {
            "hotel_ids": sorted(hotel_ids),
            "date_range": date_range,
            "analysis_type": analysis_type
        }
        key_str = json.dumps(key_data, sort_keys=True)
        
        # 使用MD5生成缓存键
        return f"ai_analysis:{hashlib.md5(key_str.encode()).hexdigest()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """从缓存获取结果
        
        Args:
            cache_key: 缓存键
            
        Returns:
            缓存的结果，如果不存在则返回None
        """
        if not self.redis_client:
            return None
            
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
        return None
    
    def _cache_result(self, cache_key: str, result: Dict[str, Any]) -> None:
        """缓存结果
        
        Args:
            cache_key: 缓存键
            result: 要缓存的结果
        """
        if not self.redis_client:
            return
            
        self.redis_client.setex(
            cache_key,
            self.cache_ttl,
            json.dumps(result, ensure_ascii=False)
        )
    
    def _get_hotel_data(self, hotel_ids: List[int], date_range: Dict[str, str]) -> Dict[str, Any]:
        """获取酒店数据和KPI指标
        
        Args:
            hotel_ids: 酒店ID列表
            date_range: 日期范围，包含start_date和end_date
            
        Returns:
            酒店数据字典
        """
        result = {
            "hotels": [],
            "kpi_summary": {},
            "period": date_range
        }
        
        # 获取日期范围
        start_date = date_range.get("start_date")
        end_date = date_range.get("end_date")
        
        if not start_date or not end_date:
            return result
            
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # 获取酒店数据
        hotels = []
        for hotel_id in hotel_ids:
            hotel_data = self.data_repository.get_hotel_data_by_id(hotel_id)
            if hotel_data:
                hotels.append(hotel_data)
        
        # 计算当前周期的KPI指标
        occupancy_data = self.data_repository.calculate_occupancy_rate(
            start_date=start_date_dt,
            end_date=end_date_dt
        )
        
        revenue_metrics = self.data_repository.calculate_revenue_metrics(
            start_date=start_date_dt,
            end_date=end_date_dt
        )
        
        # 获取上一周期数据（用于对比）
        days_diff = (end_date_dt - start_date_dt).days + 1
        
        prev_end_date = start_date_dt - timedelta(days=1)
        prev_start_date = prev_end_date - timedelta(days=days_diff-1)
        
        # 计算上一周期的KPI指标
        prev_occupancy_data = self.data_repository.calculate_occupancy_rate(
            start_date=prev_start_date,
            end_date=prev_end_date
        )
        
        prev_revenue_metrics = self.data_repository.calculate_revenue_metrics(
            start_date=prev_start_date,
            end_date=prev_end_date
        )
        
        result["previous_period"] = {
            "start_date": prev_start_date.strftime("%Y-%m-%d"),
            "end_date": prev_end_date.strftime("%Y-%m-%d")
        }
        
        # 处理酒店数据
        for hotel_data in hotels:
            hotel_metrics = self.db.query(HotelData).filter(
                HotelData.hotel_name == hotel_data.hotel_name,
                HotelData.date_recorded >= start_date_dt,
                HotelData.date_recorded <= end_date_dt
            ).all()
            
            for hotel in hotel_metrics:
                result["hotels"].append({
                    "id": hotel.id,
                    "name": hotel.hotel_name,
                    "location": hotel.location,
                    "date": hotel.date_recorded.strftime("%Y-%m-%d"),
                    "occupancy_rate": hotel.occupancy_rate,
                    "adr": hotel.adr,
                    "revpar": hotel.revpar,
                    "revenue": hotel.revenue,
                    "cost": hotel.cost if hasattr(hotel, 'cost') else None,
                    "profit": hotel.profit if hasattr(hotel, 'profit') else None
                })
        
        # 计算KPI汇总
        avg_occupancy = sum(item["occupancy_rate"] for item in occupancy_data) / len(occupancy_data) if occupancy_data else 0
        avg_adr = sum(item["adr"] for item in revenue_metrics) / len(revenue_metrics) if revenue_metrics else 0
        avg_revpar = sum(item["revpar"] for item in revenue_metrics) / len(revenue_metrics) if revenue_metrics else 0
        total_revenue = sum(item["revenue"] for item in revenue_metrics) if revenue_metrics else 0
        
        current_kpis = {
            "occupancy_rate": avg_occupancy,
            "adr": avg_adr,
            "revpar": avg_revpar,
            "revenue": total_revenue
        }
        
        # 计算上一周期KPI
        prev_avg_occupancy = sum(item["occupancy_rate"] for item in prev_occupancy_data) / len(prev_occupancy_data) if prev_occupancy_data else 0
        prev_avg_adr = sum(item["adr"] for item in prev_revenue_metrics) / len(prev_revenue_metrics) if prev_revenue_metrics else 0
        prev_avg_revpar = sum(item["revpar"] for item in prev_revenue_metrics) / len(prev_revenue_metrics) if prev_revenue_metrics else 0
        prev_total_revenue = sum(item["revenue"] for item in prev_revenue_metrics) if prev_revenue_metrics else 0
        
        prev_kpis = {
            "occupancy_rate": prev_avg_occupancy,
            "adr": prev_avg_adr,
            "revpar": prev_avg_revpar,
            "revenue": prev_total_revenue
        }
        
        # 计算同比变化
        changes = {}
        for key in current_kpis:
            if prev_kpis[key] and prev_kpis[key] != 0:
                changes[key] = ((current_kpis[key] - prev_kpis[key]) / prev_kpis[key]) * 100
            else:
                changes[key] = 0
        
        result["kpi_summary"] = {
            "current": current_kpis,
            "previous": prev_kpis,
            "changes": changes
        }
        
        # 获取高级KPI指标
        # 不再需要传递prev_hotels，因为我们已经有了更好的数据源
        self._add_advanced_kpis(result, hotels, [])
        
        return result
    
    def _add_advanced_kpis(self, result: Dict[str, Any], hotels: List[HotelData], 
                          _unused_param: List[Any] = None) -> None:
        """添加高级KPI指标
        
        Args:
            result: 结果字典
            hotels: 当前酒店数据列表
            _unused_param: 不再使用的参数，保留是为了兼容性
        """
        # 获取日期范围
        period = result.get("period", {})
        start_date = period.get("start_date")
        end_date = period.get("end_date")
        
        if not start_date or not end_date:
            return
            
        start_date_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_date_dt = datetime.strptime(end_date, "%Y-%m-%d")
        
        # 使用数据仓库获取酒店性能比较数据
        hotel_performance = self.data_repository.get_hotel_performance_comparison(
            start_date=start_date_dt,
            end_date=end_date_dt,
            metrics=["occupancy_rate", "adr", "revpar"]
        )
        
        # 转换为地区KPI格式
        region_kpis = {}
        for hotel in hotels:
            region = hotel.location.split(',')[-1].strip() if hotel.location else "未知"
            if region not in region_kpis:
                region_kpis[region] = {
                    "occupancy_rate": 0,
                    "adr": 0,
                    "revpar": 0,
                    "revenue": 0,
                    "hotel_count": 0
                }
            
            # 增加酒店计数
            region_kpis[region]["hotel_count"] += 1
        
        # 计算每个地区的平均值
        for region in region_kpis:
            # 过滤该地区的酒店数据
            region_hotels = [h for h in hotels if (h.location and h.location.split(',')[-1].strip() == region) or (not h.location and region == "未知")]
            
            if region_hotels:
                region_kpis[region]["occupancy_rate"] = sum(h.occupancy_rate for h in region_hotels if h.occupancy_rate is not None) / len(region_hotels)
                region_kpis[region]["adr"] = sum(h.adr for h in region_hotels if h.adr is not None) / len(region_hotels)
                region_kpis[region]["revpar"] = sum(h.revpar for h in region_hotels if h.revpar is not None) / len(region_hotels)
                region_kpis[region]["revenue"] = sum(h.revenue for h in region_hotels if h.revenue is not None)
        
        result["regional_kpis"] = region_kpis
        
        # 获取趋势数据
        trend_data = self.data_repository.get_trend_analysis(
            start_date=start_date_dt,
            end_date=end_date_dt,
            metric="occupancy_rate",
            group_by="day"
        )
        
        # 格式化为每日KPI格式
        if trend_data and trend_data.get("trend_data"):
            daily_kpis = {}
            
            # 获取每日入住率
            for item in trend_data["trend_data"]:
                date_str = item["date"]
                daily_kpis[date_str] = {
                    "occupancy_rate": item["value"]
                }
            
            # 获取每日ADR
            adr_trend = self.data_repository.get_trend_analysis(
                start_date=start_date_dt,
                end_date=end_date_dt,
                metric="adr",
                group_by="day"
            )
            
            for item in adr_trend.get("trend_data", []):
                date_str = item["date"]
                if date_str in daily_kpis:
                    daily_kpis[date_str]["adr"] = item["value"]
            
            # 获取每日RevPAR
            revpar_trend = self.data_repository.get_trend_analysis(
                start_date=start_date_dt,
                end_date=end_date_dt,
                metric="revpar",
                group_by="day"
            )
            
            for item in revpar_trend.get("trend_data", []):
                date_str = item["date"]
                if date_str in daily_kpis:
                    daily_kpis[date_str]["revpar"] = item["value"]
            
            # 获取每日收入
            revenue_trend = self.data_repository.get_trend_analysis(
                start_date=start_date_dt,
                end_date=end_date_dt,
                metric="revenue",
                group_by="day"
            )
            
            for item in revenue_trend.get("trend_data", []):
                date_str = item["date"]
                if date_str in daily_kpis:
                    daily_kpis[date_str]["revenue"] = item["value"]
            
            result["daily_kpis"] = daily_kpis
    
    # _calculate_average 方法已被删除，因为我们现在使用数据仓库进行计算
    
    def _build_prompt(self, hotel_data: Dict[str, Any], analysis_type: str) -> str:
        """构建AI提示词
        
        Args:
            hotel_data: 酒店数据
            analysis_type: 分析类型
            
        Returns:
            提示词字符串
        """
        # 获取提示词模板
        template = self._get_prompt_template(analysis_type)
        
        # 获取KPI汇总
        kpi_summary = hotel_data.get("kpi_summary", {})
        current_kpis = kpi_summary.get("current", {})
        changes = kpi_summary.get("changes", {})
        
        # 格式化KPI数据
        occupancy_rate = current_kpis.get("occupancy_rate", 0)
        occupancy_change = changes.get("occupancy_rate", 0)
        adr = current_kpis.get("adr", 0)
        adr_change = changes.get("adr", 0)
        revpar = current_kpis.get("revpar", 0)
        revpar_change = changes.get("revpar", 0)
        revenue = current_kpis.get("revenue", 0)
        revenue_change = changes.get("revenue", 0)
        
        # 填充模板
        prompt = template.format(
            hotel_count=len(hotel_data.get('hotels', [])),
            start_date=hotel_data.get('period', {}).get('start_date'),
            end_date=hotel_data.get('period', {}).get('end_date'),
            occupancy_rate=occupancy_rate,
            occupancy_change=occupancy_change,
            adr=adr,
            adr_change=adr_change,
            revpar=revpar,
            revpar_change=revpar_change,
            revenue=revenue,
            revenue_change=revenue_change,
            data_details=json.dumps(hotel_data, ensure_ascii=False, indent=2)
        )
        
        return prompt
    
    def _get_prompt_template(self, analysis_type: str) -> str:
        """获取提示词模板
        
        Args:
            analysis_type: 分析类型
            
        Returns:
            提示词模板字符串
        """
        # 基础模板
        base_template = """
你是一位资深的酒店业数据分析专家，请基于以下酒店运营数据进行深度分析：

**数据概览：**
- 酒店数量：{hotel_count}家
- 分析周期：{start_date} 至 {end_date}
- 主要指标：
  - 平均入住率: {occupancy_rate:.2f}% ({'+' if occupancy_change and occupancy_change > 0 else ''}{occupancy_change:.2f}% 同比)
  - 平均房价(ADR): {adr:.2f} ({'+' if adr_change and adr_change > 0 else ''}{adr_change:.2f}% 同比)
  - 每可用房收入(RevPAR): {revpar:.2f} ({'+' if revpar_change and revpar_change > 0 else ''}{revpar_change:.2f}% 同比)
  - 总收入: {revenue:.2f} ({'+' if revenue_change and revenue_change > 0 else ''}{revenue_change:.2f}% 同比)

{analysis_sections}

**输出要求：**
- 提供具体数据支撑
- 给出可执行的建议
- 突出关键洞察
- 使用图表说明（如需要）

**数据详情：**
{data_details}
"""
        
        # 针对不同分析类型的分析部分
        analysis_sections = {
            "comprehensive": """**请从以下维度进行分析：**

1. **收入表现分析**
   - 识别收入增长/下降趋势
   - 分析季节性影响因素
   - 对比同期历史数据

2. **运营效率评估**
   - 入住率优化建议
   - 房价策略分析
   - 成本控制要点

3. **市场竞争分析**
   - 竞争优势识别
   - 市场定位建议
   - 差异化策略

4. **未来预测与建议**
   - 短期业绩预测（3个月）
   - 长期发展建议（12个月）
   - 风险提示与应对策略""",
            
            "revenue": """**请进行深入的收入表现分析：**

1. **收入趋势分析**
   - 收入增长/下降趋势识别
   - 各收入来源贡献分析
   - 收入波动原因分析

2. **季节性与周期性分析**
   - 季节性影响因素识别
   - 周期性模式分析
   - 特殊事件影响评估

3. **历史对比分析**
   - 同比增长/下降分析
   - 历史最佳/最差表现对比
   - 长期收入趋势评估

4. **收入优化建议**
   - 收入管理策略建议
   - 价格弹性分析
   - 收入多元化建议""",
            
            "operational": """**请进行全面的运营效率评估：**

1. **入住率分析**
   - 入住率趋势分析
   - 影响入住率的关键因素
   - 入住率优化策略建议

2. **房价策略分析**
   - 当前房价策略评估
   - 价格弹性分析
   - 动态定价建议

3. **成本控制分析**
   - 主要成本项目分析
   - 成本效率评估
   - 成本优化建议

4. **运营效率指标**
   - 关键运营指标评估
   - 效率瓶颈识别
   - 效率提升建议""",
            
            "competitive": """**请进行详细的市场竞争分析：**

1. **竞争优势分析**
   - 核心竞争优势识别
   - 相对竞争地位评估
   - 优势强化建议

2. **市场定位分析**
   - 当前市场定位评估
   - 目标客户群体分析
   - 定位优化建议

3. **差异化策略分析**
   - 当前差异化要素评估
   - 差异化效果分析
   - 差异化策略建议

4. **竞争对手分析**
   - 主要竞争对手识别
   - 竞争对手策略分析
   - 应对策略建议""",
            
            "forecast": """**请进行详细的未来预测与建议：**

1. **短期预测（3个月）**
   - 关键指标预测
   - 可能的波动因素
   - 短期策略建议

2. **中期预测（6-12个月）**
   - 市场趋势预测
   - 关键指标预期
   - 中期策略建议

3. **长期发展（1-3年）**
   - 行业发展趋势
   - 长期增长机会
   - 战略发展建议

4. **风险分析与应对**
   - 潜在风险识别
   - 风险影响评估
   - 风险应对策略"""
        }
        
        # 获取对应的分析部分，如果不存在则使用综合分析
        section = analysis_sections.get(analysis_type, analysis_sections["comprehensive"])
        
        # 填充模板
        return base_template.format(analysis_sections=section, **{})
    
    def _call_ai_service(self, prompt: str) -> str:
        """调用AI服务
        
        Args:
            prompt: 提示词
            
        Returns:
            AI响应内容
        """
        try:
            # 准备请求参数
            api_url = settings.AI_API_URL
            api_key = settings.AI_API_KEY
            
            if not api_key:
                raise AIServiceError("未配置AI API密钥")
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            payload = {
                "model": settings.AI_MODEL,
                "messages": [
                    {"role": "system", "content": "你是一位专业的酒店业数据分析师，擅长分析酒店运营数据并提供洞察和建议。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 4000
            }
            
            # 发送请求
            with httpx.Client(timeout=settings.AI_TIMEOUT) as client:
                response = client.post(api_url, json=payload, headers=headers)
                response.raise_for_status()
                
                # 解析响应
                result = response.json()
                
                # 提取回答
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    raise AIServiceError("AI响应格式无效")
                    
        except httpx.RequestError as e:
            logger.error(f"AI服务请求错误: {str(e)}")
            raise AIServiceError(f"AI服务请求错误: {str(e)}")
            
        except httpx.HTTPStatusError as e:
            logger.error(f"AI服务HTTP错误: {str(e)}")
            
            # 处理常见HTTP错误
            if e.response.status_code == 401:
                raise AIServiceError("AI服务认证失败，请检查API密钥")
            elif e.response.status_code == 429:
                raise AIServiceError("AI服务请求过于频繁，请稍后再试")
            elif e.response.status_code >= 500:
                raise AIServiceError("AI服务暂时不可用，请稍后再试")
            else:
                raise AIServiceError(f"AI服务HTTP错误: {str(e)}")
            
        except Exception as e:
            logger.error(f"调用AI服务失败: {str(e)}")
            raise AIServiceError(f"调用AI服务失败: {str(e)}")
    
    def _parse_ai_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """解析AI响应
        
        Args:
            response: AI响应内容
            analysis_type: 分析类型
            
        Returns:
            解析后的结果字典
        """
        # 基本结构
        result = {
            "full_analysis": response,
            "summary": "",
            "key_insights": [],
            "recommendations": []
        }
        
        try:
            # 提取摘要（假设前两段是摘要）
            paragraphs = [p for p in response.split('\n\n') if p.strip()]
            if len(paragraphs) >= 2:
                result["summary"] = '\n\n'.join(paragraphs[:2])
            
            # 提取关键洞察
            insights_section = self._extract_section(response, ["关键洞察", "主要发现", "核心发现", "Key Insights"])
            if insights_section:
                # 尝试从列表项中提取
                insights = self._extract_list_items(insights_section)
                if insights:
                    result["key_insights"] = insights
            
            # 提取建议
            recommendations_section = self._extract_section(response, ["建议", "推荐", "策略建议", "Recommendations"])
            if recommendations_section:
                # 尝试从列表项中提取
                recommendations = self._extract_list_items(recommendations_section)
                if recommendations:
                    result["recommendations"] = recommendations
            
            # 根据分析类型添加特定结构
            if analysis_type == "revenue":
                result["revenue_analysis"] = self._extract_section(response, ["收入表现", "收入分析", "Revenue Analysis"])
            elif analysis_type == "operational":
                result["operational_analysis"] = self._extract_section(response, ["运营效率", "运营分析", "Operational Analysis"])
            elif analysis_type == "competitive":
                result["competitive_analysis"] = self._extract_section(response, ["市场竞争", "竞争分析", "Competitive Analysis"])
            elif analysis_type == "forecast":
                result["forecast"] = self._extract_section(response, ["未来预测", "预测分析", "Forecast"])
            
            return result
            
        except Exception as e:
            logger.warning(f"解析AI响应时出错: {str(e)}")
            # 如果解析失败，返回原始响应
            return result
    
    def _extract_section(self, text: str, section_titles: List[str]) -> Optional[str]:
        """从文本中提取特定部分
        
        Args:
            text: 文本内容
            section_titles: 部分标题列表
            
        Returns:
            提取的部分内容，如果未找到则返回None
        """
        lines = text.split('\n')
        start_idx = -1
        end_idx = len(lines)
        
        # 查找部分开始
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(title.lower() in line_lower for title in section_titles):
                start_idx = i
                break
        
        if start_idx == -1:
            return None
        
        # 查找部分结束（下一个标题）
        for i in range(start_idx + 1, len(lines)):
            if lines[i].strip() and (lines[i].startswith('#') or lines[i].startswith('**')):
                end_idx = i
                break
        
        # 提取部分内容
        section_content = '\n'.join(lines[start_idx:end_idx]).strip()
        return section_content
    
    def _extract_list_items(self, text: str) -> List[str]:
        """从文本中提取列表项
        
        Args:
            text: 文本内容
            
        Returns:
            列表项列表
        """
        items = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # 匹配列表项（- 或 * 或 1. 等开头）
            if line and (line.startswith('-') or line.startswith('*') or (len(line) > 2 and line[0].isdigit() and line[1] == '.')):
                # 去除列表标记
                item = line[line.find(' ')+1:].strip()
                if item:
                    items.append(item)
        
        return items 