"""API数据模型

定义了API接口使用的请求和响应数据模型。
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class BacktestData(BaseModel):
    start_date: str = Field(
        ..., 
        description="回测开始日期，格式：YYYY-MM-DD",
        example="2023-01-01"
    )
    end_date: str = Field(
        ..., 
        description="回测结束日期，格式：YYYY-MM-DD",
        example="2023-12-31"
    )

class Strategy(BaseModel):
    exclude_conditions: List[str] = Field(
        ..., 
        description="排除条件列表",
        example=["低于面值", "已到期"]
    )
    score_factors: List[str] = Field(
        ..., 
        description="评分因子列表",
        example=["到期收益率", "剩余期限"]
    )
    weights: List[float] = Field(
        ..., 
        description="因子权重列表",
        example=[0.7, 0.3]
    )
    hold_num: int = Field(
        ..., 
        description="持仓数量，必须大于0", 
        gt=0,
        example=20
    )
    stop_profit: float = Field(
        ..., 
        description="止盈比例，必须大于等于0", 
        ge=0,
        example=0.2
    )
    fee_rate: float = Field(
        ..., 
        description="交易费率，必须大于等于0", 
        ge=0,
        example=0.003
    )

class StrategyConfig(Strategy):
    """扩展的策略配置，包含更多可选参数"""
    name: Optional[str] = Field(None, description="策略名称")
    description: Optional[str] = Field(None, description="策略描述")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

class BacktestRequest(BaseModel):
    data: BacktestData = Field(..., description="回测时间范围")
    strategy: Strategy = Field(..., description="策略参数")

class BacktestResult(BaseModel):
    """回测结果详情"""
    annual_return: float = Field(..., description="年化收益率")
    max_drawdown: float = Field(..., description="最大回撤")
    sharpe_ratio: float = Field(..., description="夏普比率")
    sortino_ratio: float = Field(..., description="索提诺比率")
    win_rate: float = Field(..., description="胜率")
    trade_count: int = Field(..., description="交易次数")
    avg_hold_days: float = Field(..., description="平均持仓天数")
    daily_returns: List[float] = Field(..., description="每日收益率序列")
    positions: Dict[str, List[str]] = Field(..., description="每日持仓")
    trades: List[Dict] = Field(..., description="交易记录")

class BacktestResponse(BaseModel):
    """回测响应"""
    request: BacktestRequest = Field(..., description="回测请求参数")
    result: BacktestResult = Field(..., description="回测结果")
    success: bool = Field(..., description="是否成功")
    message: str = Field("", description="错误信息")
    elapsed_time: float = Field(..., description="耗时(秒)") 