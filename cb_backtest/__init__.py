"""
CB Backtest Package

用于可转债回测的Python包。
"""

# Core components
from .core.backtester import CBBacktester
from .core.engine import FactorEngine
from .core.eval import evaluate_performance
from .core.single_runner import SingleRunner
from .core.batch_runner import BatchRunner

# API components
from .api.models import BacktestRequest, BacktestData, Strategy
from .api.app import app

__version__ = '0.1.0'

__all__ = [
    # Core components
    "CBBacktester",
    "FactorEngine",
    "evaluate_performance",
    "SingleRunner",
    "BatchRunner",
    
    # API components
    "BacktestRequest",
    "BacktestData",
    "Strategy",
    "app",
]



