# 绩效评估模块

import pandas as pd
import numpy as np
import quantstats as qs

def evaluate_performance(df: pd.DataFrame, benchmark_series: pd.Series = None, html_output_path: str = None) -> dict:
    """
    评估回测结果的绩效指标
    
    Args:
        df: 包含time_return列的DataFrame，索引为日期
        benchmark_series: 基准收益率序列（可选）
        html_output_path: HTML报告输出路径（可选）
        
    Returns:
        dict: 包含各项绩效指标的字典
    """
    result = {}

    # 输入验证
    if df is None or df.empty:
        return {
            "error": "Empty result DataFrame",
            "final_nav": 1.0,
            "annual_return": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "sortino_ratio": 0.0,
            "win_rate": 0.0,
            "trade_count": 0,
            "avg_hold_days": 0,
            "total_days": 0,
            "start_date": None,
            "end_date": None,
            "daily_returns": {},
            "positions": {},
            "trades": []
        }

    if 'time_return' not in df.columns:
        return {
            "error": "Missing 'time_return' column in result DataFrame",
            "final_nav": 1.0,
            "annual_return": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "sortino_ratio": 0.0,
            "win_rate": 0.0,
            "trade_count": 0,
            "avg_hold_days": 0,
            "total_days": 0,
            "start_date": None,
            "end_date": None,
            "daily_returns": {},
            "positions": {},
            "trades": []
        }

    df = df.copy()
    returns = df['time_return']
    
    # 确保索引是日期类型
    if not isinstance(returns.index, pd.DatetimeIndex):
        try:
            returns.index = pd.to_datetime(returns.index)
        except Exception as e:
            return {
                "error": f"Failed to convert index to datetime: {str(e)}",
                "final_nav": 1.0,
                "annual_return": 0.0,
                "max_drawdown": 0.0,
                "volatility": 0.0,
                "sharpe": 0.0,
                "total_days": 0,
                "start_date": None,
                "end_date": None
            }

    # 计算回测区间的天数
    days = (returns.index[-1] - returns.index[0]).days if len(returns) > 1 else 0
    years = days / 365.0

    # 基础指标
    final_nav = (1 + returns).cumprod().iloc[-1]
    result['final_nav'] = final_nav
    # 年化收益率 = (最终净值)^(1/年数) - 1
    result['annual_return'] = np.power(final_nav, 1/years) - 1 if years > 0 else 0
    result['max_drawdown'] = qs.stats.max_drawdown(returns)
    result['volatility'] = qs.stats.volatility(returns)
    result['sharpe'] = qs.stats.sharpe(returns)
    result['sortino_ratio'] = qs.stats.sortino(returns)
    result['win_rate'] = len(returns[returns > 0]) / len(returns)
    result['trade_count'] = len(returns)
    result['avg_hold_days'] = 1  # 默认为1天，因为是日频交易
    
    # 添加回测区间信息
    result['start_date'] = returns.index[0].strftime('%Y-%m-%d') if len(returns) > 0 else None
    result['end_date'] = returns.index[-1].strftime('%Y-%m-%d') if len(returns) > 0 else None
    result['total_days'] = days

    # 添加每日收益率序列（转换为日期和收益率的键值对）
    result['daily_returns'] = {date.strftime('%Y-%m-%d'): float(ret) for date, ret in returns.items()}
    
    # 添加空的持仓和交易记录（因为这些信息在回测过程中应该由回测器提供）
    result['positions'] = {}
    result['trades'] = []

    # # 生成 HTML 报告（如指定）
    # if html_output_path:
    #     if benchmark_series is not None:
    #         benchmark_series.index = pd.to_datetime(benchmark_series.index)
    #         qs.reports.html(returns, benchmark=benchmark_series, output=html_output_path, title="Strategy Report")
    #     else:
    #         qs.reports.html(returns, output=html_output_path, title="Strategy Report")

    return result