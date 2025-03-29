"""数据验证模块

提供数据验证和检查相关的工具函数。
"""

from typing import List, Dict, Any, Union
import numpy as np
from datetime import date
from .date import parse_date
from .logger import logger

def validate_weights(
    weights: Union[List[float], np.ndarray], 
    tolerance: float = 1e-6,
    allow_negative: bool = False
) -> bool:
    """验证权重是否合法
    
    Args:
        weights: 权重列表或数组
        tolerance: 误差容忍度
        allow_negative: 是否允许负权重
        
    Returns:
        是否合法
        
    Raises:
        ValueError: 权重包含非数值时抛出
    """
    try:
        weights = np.array(weights, dtype=float)
    except Exception as e:
        logger.error("权重包含非数值")
        raise ValueError("权重必须为数值") from e
        
    if not allow_negative and np.any(weights < 0):
        return False
        
    return abs(np.sum(weights) - 1.0) < tolerance

def validate_date_order(
    start_date: Union[str, date], 
    end_date: Union[str, date]
) -> bool:
    """验证开始日期是否早于结束日期
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        
    Returns:
        是否合法
    """
    try:
        start = parse_date(start_date) if isinstance(start_date, str) else start_date
        end = parse_date(end_date) if isinstance(end_date, str) else end_date
        return start <= end
    except Exception as e:
        logger.error(f"日期验证错误: {str(e)}")
        return False

def validate_dict_keys(
    d: Dict[str, Any],
    required_keys: List[str],
    optional_keys: List[str] = None
) -> bool:
    """验证字典是否包含必需的键
    
    Args:
        d: 待验证字典
        required_keys: 必需的键列表
        optional_keys: 可选的键列表
        
    Returns:
        是否合法
    """
    if not isinstance(d, dict):
        return False
        
    all_keys = set(d.keys())
    required = set(required_keys)
    optional = set(optional_keys or [])
    
    # 检查是否包含所有必需的键
    if not required.issubset(all_keys):
        return False
        
    # 检查是否存在未知的键
    if not all_keys.issubset(required.union(optional)):
        return False
        
    return True 