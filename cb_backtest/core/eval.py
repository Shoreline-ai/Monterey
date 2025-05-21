# 绩效评估模块

import pandas as pd
import numpy as np
import quantstats as qs

def evaluate_performance(df: pd.DataFrame, benchmark_series: pd.Series = None, html_output_path: str = None) -> dict:
    """
    Evaluate the performance of a strategy using various metrics.
    
    Args:
        df (pd.DataFrame): DataFrame containing the strategy returns
        benchmark_series (pd.Series, optional): Benchmark returns series
        html_output_path (str, optional): Path to save HTML report
        
    Returns:
        dict: Dictionary containing performance metrics
    """
    result = {}
    
    # 提取收益率序列
    if isinstance(df, pd.Series):
        returns = df
    elif isinstance(df, pd.DataFrame) and 'returns' in df.columns:
        returns = df['returns']
    else:
        print("Error: Input data format not recognized")
        return {
            "error": "Input data format not recognized",
            "final_nav": 1.0,
            "annual_return": 0.0,
            "max_drawdown": 0.0,
            "volatility": 0.0,
            "sharpe": 0.0,
            "total_days": 0,
            "start_date": None,
            "end_date": None
        }
    
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

    # 数据预处理
    clean_returns = returns.astype(float)
    clean_returns = clean_returns.sort_index()
    
    # 处理重复的日期索引
    if clean_returns.index.duplicated().any():
        clean_returns = clean_returns.resample('D').last()
    
    # 处理基准数据
    clean_benchmark = None
    if benchmark_series is not None:
        clean_benchmark = benchmark_series.astype(float)
        if not isinstance(clean_benchmark.index, pd.DatetimeIndex):
            clean_benchmark.index = pd.to_datetime(clean_benchmark.index)
        clean_benchmark = clean_benchmark.sort_index()
        
        # 对齐数据
        clean_benchmark = clean_benchmark.reindex(clean_returns.index)
        
        # 处理重复的日期索引
        if clean_benchmark.index.duplicated().any():
            clean_benchmark = clean_benchmark.resample('D').last()

    # 计算回测区间的天数
    days = (clean_returns.index[-1] - clean_returns.index[0]).days if len(clean_returns) > 1 else 0
    years = days / 365.0

    # 基础指标
    final_nav = (1 + clean_returns).cumprod().iloc[-1]
    result['final_nav'] = final_nav
    # 年化收益率 = (最终净值)^(1/年数) - 1
    result['annual_return'] = np.power(final_nav, 1/years) - 1 if years > 0 else 0
    result['max_drawdown'] = qs.stats.max_drawdown(clean_returns)
    result['volatility'] = qs.stats.volatility(clean_returns)
    result['sharpe'] = qs.stats.sharpe(clean_returns)
    result['sortino_ratio'] = qs.stats.sortino(clean_returns)
    result['win_rate'] = len(clean_returns[clean_returns > 0]) / len(clean_returns)
    result['trade_count'] = len(clean_returns)
    result['avg_hold_days'] = 1  # 默认为1天，因为是日频交易
    
    # 添加回测区间信息
    result['start_date'] = clean_returns.index[0].strftime('%Y-%m-%d') if len(clean_returns) > 0 else None
    result['end_date'] = clean_returns.index[-1].strftime('%Y-%m-%d') if len(clean_returns) > 0 else None
    result['total_days'] = days

    # 添加每日收益率序列（转换为日期和收益率的键值对）
    result['daily_returns'] = {date.strftime('%Y-%m-%d'): float(ret) for date, ret in clean_returns.items()}
    
    # 添加空的持仓和交易记录（因为这些信息在回测过程中应该由回测器提供）
    result['positions'] = {}
    result['trades'] = []

    # 生成 HTML 报告（如指定）
    if html_output_path:
        try:
            if clean_benchmark is not None:
                qs.reports.html(clean_returns, 
                              benchmark=clean_benchmark, 
                              output=html_output_path, 
                              title="Strategy Report",
                              periods_per_year=252)
            else:
                qs.reports.html(clean_returns, 
                              output=html_output_path, 
                              title="Strategy Report",
                              periods_per_year=252)
        except Exception as e:
            print(f"Warning: Failed to generate HTML report: {e}")

    return result