"""性能指标计算模块

提供各种投资组合性能指标的计算功能。
"""

import numpy as np
import pandas as pd
from typing import Optional, Tuple
from .logger import logger

def calculate_drawdown(returns: pd.Series) -> pd.Series:
    """计算回撤序列
    
    Args:
        returns: 收益率序列
        
    Returns:
        回撤序列
        
    Raises:
        ValueError: 输入数据无效时抛出
    """
    if not isinstance(returns, pd.Series):
        raise ValueError("输入必须是pandas.Series类型")
        
    try:
        cum_returns = (1 + returns).cumprod()
        rolling_max = cum_returns.expanding().max()
        drawdowns = cum_returns / rolling_max - 1
        return drawdowns
    except Exception as e:
        logger.error(f"回撤计算错误: {str(e)}")
        raise

def calculate_sharpe_ratio(
    returns: pd.Series, 
    risk_free_rate: float = 0.03,
    periods_per_year: int = 252,
    min_periods: int = 30
) -> float:
    """计算夏普比率
    
    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率(年化)
        periods_per_year: 年化系数
        min_periods: 最小样本数量
        
    Returns:
        夏普比率
        
    Raises:
        ValueError: 样本数量不足时抛出
    """
    if len(returns) < min_periods:
        raise ValueError(f"样本数量不足: {len(returns)} < {min_periods}")
        
    try:
        excess_returns = returns - risk_free_rate / periods_per_year
        return np.sqrt(periods_per_year) * excess_returns.mean() / returns.std()
    except Exception as e:
        logger.error(f"夏普比率计算错误: {str(e)}")
        raise

def calculate_sortino_ratio(
    returns: pd.Series,
    risk_free_rate: float = 0.03,
    periods_per_year: int = 252,
    min_periods: int = 30
) -> float:
    """计算索提诺比率
    
    Args:
        returns: 收益率序列
        risk_free_rate: 无风险利率(年化)
        periods_per_year: 年化系数
        min_periods: 最小样本数量
        
    Returns:
        索提诺比率
    """
    if len(returns) < min_periods:
        raise ValueError(f"样本数量不足: {len(returns)} < {min_periods}")
        
    try:
        excess_returns = returns - risk_free_rate / periods_per_year
        downside_returns = returns[returns < 0]
        if len(downside_returns) == 0:
            return np.inf
        return np.sqrt(periods_per_year) * excess_returns.mean() / downside_returns.std()
    except Exception as e:
        logger.error(f"索提诺比率计算错误: {str(e)}")
        raise

def calculate_max_drawdown(returns: pd.Series) -> Tuple[float, Optional[pd.Timestamp], Optional[pd.Timestamp]]:
    """计算最大回撤及其发生时间
    
    Args:
        returns: 收益率序列
        
    Returns:
        (最大回撤, 开始时间, 结束时间)的元组
    """
    try:
        drawdowns = calculate_drawdown(returns)
        max_dd = drawdowns.min()
        
        if max_dd == 0:
            return 0.0, None, None
            
        end_idx = drawdowns.idxmin()
        peak_idx = (1 + returns).cumprod().loc[:end_idx].idxmax()
        
        return float(max_dd), peak_idx, end_idx
    except Exception as e:
        logger.error(f"最大回撤计算错误: {str(e)}")
        raise 