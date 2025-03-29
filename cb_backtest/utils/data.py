"""数据处理模块

提供数据处理、计算和转换相关的工具函数。
"""

from typing import Union, Dict, Any
import numpy as np
from .logger import logger

def safe_divide(
    a: Union[float, np.ndarray], 
    b: Union[float, np.ndarray]
) -> Union[float, np.ndarray]:
    """安全除法，处理除数为零的情况
    
    Args:
        a: 被除数，可以是标量或数组
        b: 除数，可以是标量或数组
        
    Returns:
        除法结果，除数为0时返回0
    """
    try:
        if isinstance(a, (float, int)) and isinstance(b, (float, int)):
            return a / b if b != 0 else 0
        return np.divide(a, b, out=np.zeros_like(a), where=b!=0)
    except Exception as e:
        logger.error(f"除法计算错误: {str(e)}")
        raise

def round_dict(
    d: Dict[str, Any], 
    decimals: int = 4,
    skip_keys: set = None
) -> Dict[str, Any]:
    """对字典中的浮点数值进行四舍五入
    
    Args:
        d: 输入字典
        decimals: 保留小数位数
        skip_keys: 不进行四舍五入的键集合
        
    Returns:
        处理后的新字典
        
    Raises:
        ValueError: decimals为负数时抛出
    """
    if decimals < 0:
        raise ValueError(f"decimals不能为负数: {decimals}")
        
    skip_keys = skip_keys or set()
    return {
        k: (round(v, decimals) if isinstance(v, (float, np.floating)) and k not in skip_keys else v)
        for k, v in d.items()
    } 