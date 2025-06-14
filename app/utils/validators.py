import re
import logging
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
from datetime import datetime, date

logger = logging.getLogger(__name__)

class DataValidator:
    """数据验证工具类，用于验证上传的数据是否符合要求"""
    
    def __init__(self):
        # 定义常用的验证规则
        self.validation_rules = {
            "hotel_name": {
                "required": True,
                "type": "string",
                "max_length": 200
            },
            "location": {
                "required": False,
                "type": "string",
                "max_length": 200
            },
            "room_count": {
                "required": False,
                "type": "integer",
                "min_value": 0
            },
            "occupancy_rate": {
                "required": False,
                "type": "float",
                "min_value": 0,
                "max_value": 100
            },
            "revenue": {
                "required": False,
                "type": "float",
                "min_value": 0
            },
            "adr": {
                "required": False,
                "type": "float",
                "min_value": 0
            },
            "revpar": {
                "required": False,
                "type": "float",
                "min_value": 0
            },
            "date_recorded": {
                "required": False,
                "type": "date"
            }
        }
    
    def validate_dataframe(self, df: pd.DataFrame, rules: Optional[Dict] = None) -> Tuple[bool, Dict]:
        """
        验证DataFrame数据
        
        Args:
            df: 待验证的DataFrame
            rules: 自定义验证规则，如果为None则使用默认规则
            
        Returns:
            Tuple[bool, Dict]: (是否验证通过, 错误信息)
        """
        if rules is None:
            rules = self.validation_rules
        
        # 存储验证结果
        is_valid = True
        errors = {}
        
        # 检查必填字段
        for field, rule in rules.items():
            if rule.get("required", False) and field not in df.columns:
                is_valid = False
                errors[field] = f"必填字段 '{field}' 不存在"
        
        # 逐行验证数据
        for idx, row in df.iterrows():
            row_errors = self._validate_row(row, rules)
            if row_errors:
                is_valid = False
                errors[f"row_{idx+1}"] = row_errors
        
        return is_valid, errors
    
    def _validate_row(self, row: pd.Series, rules: Dict) -> Dict:
        """验证单行数据"""
        errors = {}
        
        for field, rule in rules.items():
            # 跳过不在数据中的非必填字段
            if field not in row and not rule.get("required", False):
                continue
            
            # 检查必填字段
            if rule.get("required", False) and (field not in row or pd.isna(row[field])):
                errors[field] = f"'{field}' 是必填字段"
                continue
            
            # 跳过空值的非必填字段
            if field not in row or pd.isna(row[field]):
                continue
            
            value = row[field]
            
            # 类型验证
            field_type = rule.get("type")
            if field_type:
                type_error = self._validate_type(value, field_type)
                if type_error:
                    errors[field] = type_error
                    continue
            
            # 字符串长度验证
            if field_type == "string" and "max_length" in rule:
                if len(str(value)) > rule["max_length"]:
                    errors[field] = f"'{field}' 超过最大长度 {rule['max_length']}"
            
            # 数值范围验证
            if field_type in ["integer", "float"]:
                if "min_value" in rule and value < rule["min_value"]:
                    errors[field] = f"'{field}' 小于最小值 {rule['min_value']}"
                if "max_value" in rule and value > rule["max_value"]:
                    errors[field] = f"'{field}' 大于最大值 {rule['max_value']}"
            
            # 日期格式验证
            if field_type == "date" and not isinstance(value, (date, datetime)):
                try:
                    pd.to_datetime(value)
                except:
                    errors[field] = f"'{field}' 不是有效的日期格式"
            
            # 正则表达式验证
            if "pattern" in rule:
                pattern = rule["pattern"]
                if not re.match(pattern, str(value)):
                    errors[field] = f"'{field}' 不符合格式要求"
        
        return errors
    
    def _validate_type(self, value: Any, expected_type: str) -> Optional[str]:
        """验证数据类型"""
        if expected_type == "string":
            if not isinstance(value, str):
                return f"应为字符串类型"
        elif expected_type == "integer":
            if not isinstance(value, (int, np.int64)) or isinstance(value, bool):
                try:
                    int(value)
                except:
                    return f"应为整数类型"
        elif expected_type == "float":
            if not isinstance(value, (float, int, np.float64, np.int64)):
                try:
                    float(value)
                except:
                    return f"应为数值类型"
        elif expected_type == "boolean":
            if not isinstance(value, bool):
                if isinstance(value, str):
                    if value.lower() not in ["true", "false", "0", "1", "yes", "no"]:
                        return f"应为布尔类型"
                else:
                    try:
                        bool(value)
                    except:
                        return f"应为布尔类型"
        elif expected_type == "date":
            if not isinstance(value, (date, datetime)):
                try:
                    pd.to_datetime(value)
                except:
                    return f"应为日期类型"
        
        return None
    
    def detect_anomalies(self, df: pd.DataFrame, columns: List[str] = None) -> Dict[str, List[int]]:
        """
        检测异常值
        
        Args:
            df: 数据DataFrame
            columns: 需要检测的列，如果为None则检测所有数值列
            
        Returns:
            Dict[str, List[int]]: 异常值索引字典，键为列名，值为异常值的行索引列表
        """
        anomalies = {}
        
        # 如果未指定列，则检测所有数值列
        if columns is None:
            columns = df.select_dtypes(include=["number"]).columns.tolist()
        
        for col in columns:
            if col not in df.columns:
                continue
            
            # 跳过非数值列
            if not pd.api.types.is_numeric_dtype(df[col]):
                continue
            
            # 计算四分位数
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            
            # 定义异常值边界
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            # 找出异常值
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)].index.tolist()
            
            if outliers:
                anomalies[col] = outliers
        
        return anomalies
    
    def validate_business_rules(self, df: pd.DataFrame) -> Tuple[bool, Dict]:
        """
        验证业务规则
        
        Args:
            df: 待验证的DataFrame
            
        Returns:
            Tuple[bool, Dict]: (是否验证通过, 错误信息)
        """
        is_valid = True
        errors = {}
        
        # 示例业务规则：RevPAR = ADR * 入住率
        if all(field in df.columns for field in ["revpar", "adr", "occupancy_rate"]):
            # 将入住率从百分比转换为小数
            occupancy_decimal = df["occupancy_rate"] / 100
            
            # 计算期望的RevPAR
            expected_revpar = df["adr"] * occupancy_decimal
            
            # 允许一定的误差
            tolerance = 0.01
            
            # 找出不符合规则的行
            invalid_rows = df[abs(df["revpar"] - expected_revpar) > tolerance * df["adr"]].index.tolist()
            
            if invalid_rows:
                is_valid = False
                errors["business_rule_revpar"] = {
                    "message": "RevPAR应等于ADR乘以入住率",
                    "rows": invalid_rows
                }
        
        # 可以添加更多业务规则...
        
        return is_valid, errors
    
    def suggest_corrections(self, df: pd.DataFrame, errors: Dict) -> pd.DataFrame:
        """
        根据验证错误建议数据修正
        
        Args:
            df: 原始DataFrame
            errors: 验证错误信息
            
        Returns:
            pd.DataFrame: 修正后的DataFrame
        """
        corrected_df = df.copy()
        
        # 处理行级别错误
        row_errors = {k: v for k, v in errors.items() if k.startswith("row_")}
        for row_key, field_errors in row_errors.items():
            try:
                row_idx = int(row_key.split("_")[1]) - 1
                
                # 修正各字段错误
                for field, error in field_errors.items():
                    # 处理类型错误
                    if "应为整数类型" in error:
                        try:
                            corrected_df.loc[row_idx, field] = int(float(corrected_df.loc[row_idx, field]))
                        except:
                            corrected_df.loc[row_idx, field] = 0
                    
                    elif "应为数值类型" in error:
                        try:
                            corrected_df.loc[row_idx, field] = float(corrected_df.loc[row_idx, field])
                        except:
                            corrected_df.loc[row_idx, field] = 0.0
                    
                    elif "应为日期类型" in error:
                        try:
                            corrected_df.loc[row_idx, field] = pd.to_datetime(corrected_df.loc[row_idx, field])
                        except:
                            corrected_df.loc[row_idx, field] = pd.NaT
                    
                    # 处理范围错误
                    elif "小于最小值" in error:
                        rule = self.validation_rules.get(field, {})
                        min_value = rule.get("min_value", 0)
                        corrected_df.loc[row_idx, field] = min_value
                    
                    elif "大于最大值" in error:
                        rule = self.validation_rules.get(field, {})
                        max_value = rule.get("max_value", 100)
                        corrected_df.loc[row_idx, field] = max_value
            
            except Exception as e:
                logger.error(f"修正数据错误: {str(e)}")
        
        # 处理业务规则错误
        if "business_rule_revpar" in errors:
            rule_error = errors["business_rule_revpar"]
            for row_idx in rule_error.get("rows", []):
                # 根据ADR和入住率重新计算RevPAR
                adr = corrected_df.loc[row_idx, "adr"]
                occupancy_rate = corrected_df.loc[row_idx, "occupancy_rate"] / 100
                corrected_df.loc[row_idx, "revpar"] = adr * occupancy_rate
        
        return corrected_df
