"""日志配置模块

提供日志配置和管理功能，支持自定义日志级别和格式。
"""

import logging
from typing import Optional

def setup_logger(
    name: Optional[str] = None,
    level: int = logging.INFO,
    format_str: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
) -> logging.Logger:
    """配置并返回日志器
    
    Args:
        name: 日志器名称，默认使用模块名
        level: 日志级别，默认INFO
        format_str: 日志格式字符串
        
    Returns:
        配置好的日志器实例
    """
    logger = logging.getLogger(name or __name__)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(format_str)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(level)
    return logger

logger = setup_logger('cb_backtest') 