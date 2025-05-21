import pandas as pd
import numpy as np
import quantstats as qs

def prepare_returns_for_qs(returns_series, benchmark_series=None):
    """
    Prepare returns and benchmark data for QuantStats report generation.
    Handles data cleaning, alignment, and resampling issues.
    
    Args:
        returns_series (pd.Series): Strategy returns series
        benchmark_series (pd.Series, optional): Benchmark returns series
        
    Returns:
        tuple: (clean_returns, clean_benchmark)
    """
    # 1. 处理收益率数据
    clean_returns = returns_series.copy()
    if not isinstance(clean_returns.index, pd.DatetimeIndex):
        clean_returns.index = pd.to_datetime(clean_returns.index)
    clean_returns = clean_returns.sort_index()
    clean_returns = clean_returns.astype(float)
    
    # 处理重复的日期索引
    if clean_returns.index.duplicated().any():
        clean_returns = clean_returns.groupby(clean_returns.index).last()
    
    # 2. 处理基准数据（如果有）
    clean_benchmark = None
    if benchmark_series is not None:
        clean_benchmark = benchmark_series.copy()
        if not isinstance(clean_benchmark.index, pd.DatetimeIndex):
            clean_benchmark.index = pd.to_datetime(clean_benchmark.index)
        clean_benchmark = clean_benchmark.sort_index()
        clean_benchmark = clean_benchmark.astype(float)
        
        # 对齐数据
        clean_benchmark = clean_benchmark.reindex(clean_returns.index)
        
        # 处理重复的日期索引
        if clean_benchmark.index.duplicated().any():
            clean_benchmark = clean_benchmark.groupby(clean_benchmark.index).last()
    
    return clean_returns, clean_benchmark

def generate_qs_report(returns, benchmark=None, title=None, periods_per_year=252):
    """
    Generate QuantStats report with proper data preprocessing.
    
    Args:
        returns (pd.Series): Strategy returns series
        benchmark (pd.Series, optional): Benchmark returns series
        title (str, optional): Report title
        periods_per_year (int, optional): Number of periods per year
    """
    try:
        # 预处理数据
        clean_returns, clean_benchmark = prepare_returns_for_qs(returns, benchmark)
        
        # 生成报告
        qs.reports.full(
            returns=clean_returns,
            benchmark=clean_benchmark,
            periods_per_year=periods_per_year,
            title=title
        )
        
    except Exception as e:
        print(f"Error generating QuantStats report: {e}")
        print("\nDebug information:")
        if 'clean_returns' in locals():
            print(f"Returns shape: {clean_returns.shape}")
            print(f"Returns index type: {type(clean_returns.index)}")
            print(f"Returns dtype: {clean_returns.dtype}")
            print(f"Returns has duplicates: {clean_returns.index.duplicated().any()}")
            print(f"Returns sample:\n{clean_returns.head()}")
        if 'clean_benchmark' in locals() and clean_benchmark is not None:
            print(f"Benchmark shape: {clean_benchmark.shape}")
            print(f"Benchmark index type: {type(clean_benchmark.index)}")
            print(f"Benchmark dtype: {clean_benchmark.dtype}")
            print(f"Benchmark has duplicates: {clean_benchmark.index.duplicated().any()}")
            print(f"Benchmark sample:\n{clean_benchmark.head()}")

def generate_simple_qs_report(returns, benchmark=None):
    """
    Generate a simple QuantStats report without any extra parameters.
    
    Args:
        returns (pd.Series): Strategy returns series
        benchmark (pd.Series, optional): Benchmark returns series
    """
    try:
        # 1. 确保数据类型正确
        returns = returns.astype(float)
        if not isinstance(returns.index, pd.DatetimeIndex):
            returns.index = pd.to_datetime(returns.index)
        
        if benchmark is not None:
            benchmark = benchmark.astype(float)
            if not isinstance(benchmark.index, pd.DatetimeIndex):
                benchmark.index = pd.to_datetime(benchmark.index)
            
            # 对齐数据
            benchmark = benchmark.reindex(returns.index)
        
        # 2. 生成报告
        qs.reports.full(returns, benchmark=benchmark)
        
    except Exception as e:
        print(f"Error generating simple QuantStats report: {e}")
        print("\nDebug information:")
        print(f"Returns shape: {returns.shape}")
        print(f"Returns index type: {type(returns.index)}")
        print(f"Returns dtype: {returns.dtype}")
        if benchmark is not None:
            print(f"Benchmark shape: {benchmark.shape}")
            print(f"Benchmark index type: {type(benchmark.index)}")
            print(f"Benchmark dtype: {benchmark.dtype}") 