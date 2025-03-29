"""API包

此包提供了可转债回测系统的HTTP API接口，包括：
- app: FastAPI应用程序入口
- models: 数据模型和请求/响应模式
- routes: API路由和处理函数
- middleware: 中间件
"""

from .app import app
from .models import (
    BacktestRequest,
    BacktestResponse,
    BacktestResult,
    StrategyConfig
)

__all__ = [
    'app',
    'BacktestRequest',
    'BacktestResponse',
    'BacktestResult',
    'StrategyConfig'
] 