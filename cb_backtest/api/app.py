"""可转债回测服务API"""

from typing import Dict
from fastapi import FastAPI, HTTPException
import yaml
import logging
import time
from cb_backtest.core import SingleRunner
from .models import (
    BacktestRequest, 
    BacktestResponse, 
    BacktestResult
)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 加载服务配置
with open("cb_backtest/api/config.yaml", "r") as f:
    config = yaml.safe_load(f)

app = FastAPI(title="可转债回测服务")

@app.post("/backtest", response_model=BacktestResponse)
async def run_backtest(request: BacktestRequest) -> BacktestResponse:
    """执行单次回测
    
    Args:
        request: 回测请求参数
        
    Returns:
        回测结果响应
        
    Raises:
        HTTPException: 回测执行出错时抛出
    """
    start_time = time.time()
    
    try:
        # 创建回测实例
        runner = SingleRunner(
            cb_data_path=config['data']['cb_data_path'],
            index_data_path=config['data']['index_data_path']
        )
        
        # 执行回测
        result = runner.run(
            start_date=request.data.start_date,
            end_date=request.data.end_date,
            strategy=request.strategy.dict()
        )
        
        # 构造回测结果
        backtest_result = BacktestResult(
            annual_return=result['metrics']['annual_return'],
            max_drawdown=result['metrics']['max_drawdown'],
            sharpe_ratio=result['metrics']['sharpe_ratio'],
            sortino_ratio=result['metrics']['sortino_ratio'],
            win_rate=result['metrics']['win_rate'],
            trade_count=result['metrics']['trade_count'],
            avg_hold_days=result['metrics']['avg_hold_days'],
            daily_returns=result['daily_returns'],
            positions=result['positions'],
            trades=result['trades']
        )
        
        # 构造响应
        return BacktestResponse(
            request=request,
            result=backtest_result,
            success=True,
            message="",
            elapsed_time=time.time() - start_time
        )
        
    except Exception as e:
        logger.error(f"回测执行错误: {str(e)}")
        return BacktestResponse(
            request=request,
            result=None,
            success=False,
            message=str(e),
            elapsed_time=time.time() - start_time
        )

@app.get("/health")
async def health_check() -> Dict[str, str]:
    """健康检查"""
    return {"status": "healthy"} 