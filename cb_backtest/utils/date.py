"""日期处理模块

提供日期解析、验证和范围生成等功能。
"""

from typing import List, Union
from datetime import date, datetime
import pandas as pd
from .logger import logger

def parse_date(date_str: str) -> date:
    """解析日期字符串为 date 对象
    
    Args:
        date_str: 日期字符串，支持多种格式
        
    Returns:
        date对象
        
    Raises:
        ValueError: 日期格式无效时抛出
    """
    try:
        return pd.to_datetime(date_str).date()
    except Exception as e:
        logger.error(f"日期解析错误: {date_str}")
        raise ValueError(f"无效的日期格式: {date_str}") from e

def date_range(
    start_date: Union[str, date], 
    end_date: Union[str, date],
    freq: str = 'D'
) -> List[date]:
    """生成日期范围
    
    Args:
        start_date: 开始日期
        end_date: 结束日期
        freq: 频率，默认按天('D')，支持'W'周,'M'月等
        
    Returns:
        日期列表
        
    Raises:
        ValueError: 日期顺序错误时抛出
    """
    start = parse_date(start_date) if isinstance(start_date, str) else start_date
    end = parse_date(end_date) if isinstance(end_date, str) else end_date
    
    if start > end:
        raise ValueError(f"开始日期 {start} 晚于结束日期 {end}")
        
    return pd.date_range(start, end, freq=freq).date.tolist() 