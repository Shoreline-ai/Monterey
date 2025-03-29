# 绩效评估模块

import pandas as pd
import numpy as np
import quantstats as qs

def evaluate_performance(df: pd.DataFrame, benchmark_series: pd.Series = None, html_output_path: str = None) -> dict:
    result = {}

    if 'time_return' not in df.columns:
        return {"error": "Missing 'time_return' column in result DataFrame"}

    df = df.copy()
    returns = df['time_return']
    returns.index = pd.to_datetime(returns.index)

    # 计算回测区间的天数
    days = (returns.index[-1] - returns.index[0]).days
    years = days / 365.0

    # 基础指标
    final_nav = (1 + returns).cumprod().iloc[-1]
    result['final_nav'] = final_nav
    # 年化收益率 = (最终净值)^(1/年数) - 1
    result['annual_return'] = np.power(final_nav, 1/years) - 1 if years > 0 else 0
    result['max_drawdown'] = qs.stats.max_drawdown(returns)
    result['volatility'] = qs.stats.volatility(returns)
    result['sharpe'] = qs.stats.sharpe(returns)
    # 添加回测区间信息
    result['start_date'] = returns.index[0].strftime('%Y-%m-%d')
    result['end_date'] = returns.index[-1].strftime('%Y-%m-%d')
    result['total_days'] = days

    # # 生成 HTML 报告（如指定）
    # if html_output_path:
    #     if benchmark_series is not None:
    #         benchmark_series.index = pd.to_datetime(benchmark_series.index)
    #         qs.reports.html(returns, benchmark=benchmark_series, output=html_output_path, title="Strategy Report")
    #     else:
    #         qs.reports.html(returns, output=html_output_path, title="Strategy Report")

    return result