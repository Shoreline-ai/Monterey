"""
可转债回测框架
~~~~~~~~~~~~~

这个包提供了可转债回测的核心功能：
- 单次和批量回测
- 因子策略开发
- 性能评估
- RESTful API 服务
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

__version__ = "0.1.0"

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



