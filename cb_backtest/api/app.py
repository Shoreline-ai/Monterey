"""可转债回测服务API"""

from typing import Dict
from fastapi import FastAPI, HTTPException
import yaml
import logging
import time
import os
from logging.handlers import RotatingFileHandler
from cb_backtest.core.single_runner import SingleRunner
from .models import (
    BacktestRequest, 
    BacktestResponse, 
    BacktestResult
)
import sys
from pathlib import Path

# 设置项目根目录
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 创建日志目录
log_dir = os.path.join(project_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # 输出到控制台
        RotatingFileHandler(  # 输出到文件，带轮转
            os.path.join(log_dir, 'backtest.log'),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
    ]
)

logger = logging.getLogger(__name__)

# 加载服务配置
config_path = os.path.join(project_dir, "api", "config.yaml")
try:
    with open(config_path, "r", encoding='utf-8') as f:
        config = yaml.safe_load(f)
    logger.info(f"成功加载配置文件: {config_path}")
except Exception as e:
    logger.error(f"加载配置文件失败: {str(e)}")
    config = {}

app = FastAPI(
    title="可转债回测服务",
    description="提供可转债回测相关的API服务",
    version="1.0.0"
)

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
        logger.info(f"Received backtest request: {request}")
        
        # 获取配置文件路径
        config_path = Path(__file__).parent / "config.yaml"
        if not config_path.exists():
            raise HTTPException(status_code=500, detail="Configuration file not found")
            
        # 读取配置
        with open(config_path) as f:
            config = yaml.safe_load(f)
            
        logger.info(f"Loaded config: {config}")
        
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
            sharpe=result['metrics']['sharpe'],
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
        logger.error(f"回测执行错误: {str(e)}", exc_info=True)
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