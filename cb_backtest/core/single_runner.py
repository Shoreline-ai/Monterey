from typing import Dict, Any
import logging
from .backtester import CBBacktester
from .eval import evaluate_performance

logger = logging.getLogger(__name__)

class SingleRunner:
    """单次回测运行器"""
    
    def __init__(self, cb_data_path: str, index_data_path: str):
        """
        初始化单次回测运行器
        
        Args:
            cb_data_path: 可转债数据文件路径
            index_data_path: 指数数据文件路径
        """
        self.cb_data_path = cb_data_path
        self.index_data_path = index_data_path
        self._engine = None
    
    @property
    def engine(self) -> CBBacktester:
        """懒加载回测引擎"""
        if self._engine is None:
            self._engine = CBBacktester(
                cb_data_path=self.cb_data_path,
                index_data_path=self.index_data_path
            )
        return self._engine
    
    def run(self, 
            start_date: str,
            end_date: str,
            strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行单次回测
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            strategy: 策略配置，格式如下：
                {
                    "exclude_conditions": List[str],
                    "score_factors": List[str],
                    "weights": List[float],
                    "hold_num": int,
                    "stop_profit": float,
                    "fee_rate": float
                }
        
        Returns:
            Dict[str, Any]: 回测结果，包含策略配置和指标
        """
        try:
            positions = self.engine.run_strategy(
                start_date=start_date,
                end_date=end_date,
                exclude_conditions=strategy['exclude_conditions'],
                score_factors=strategy['score_factors'],
                weights=strategy['weights'],
                hold_num=strategy['hold_num']
            )
            
            metrics = evaluate_performance(
                positions=positions,
                stop_profit=strategy['stop_profit'],
                fee_rate=strategy['fee_rate']
            )
            
            return {
                'strategy': strategy,
                'metrics': metrics
            }
            
        except Exception as e:
            logger.error(f"单次回测执行错误: {str(e)}")
            raise e 