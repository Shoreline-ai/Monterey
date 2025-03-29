from typing import Dict, List, Any
import logging
from .single_runner import SingleRunner
from .batch_runner import BatchRunner

logger = logging.getLogger(__name__)

class BacktestRunner:
    """回测运行器，提供单次和批量回测功能"""
    
    def __init__(self, cb_data_path: str, index_data_path: str):
        """
        初始化回测运行器
        
        Args:
            cb_data_path: 可转债数据文件路径
            index_data_path: 指数数据文件路径
        """
        self.cb_data_path = cb_data_path
        self.index_data_path = index_data_path
        self._single_runner = None
        self._batch_runner = None
    
    @property
    def single_runner(self) -> SingleRunner:
        """懒加载单次回测运行器"""
        if self._single_runner is None:
            self._single_runner = SingleRunner(
                cb_data_path=self.cb_data_path,
                index_data_path=self.index_data_path
            )
        return self._single_runner
    
    @property
    def batch_runner(self) -> BatchRunner:
        """懒加载批量回测运行器"""
        if self._batch_runner is None:
            self._batch_runner = BatchRunner(
                cb_data_path=self.cb_data_path,
                index_data_path=self.index_data_path
            )
        return self._batch_runner
    
    def run_backtest(self, config: Dict[str, Any]) -> Dict[str, float]:
        """
        运行单次回测
        
        Args:
            config: 配置字典，格式如下：
            {
                "data": {
                    "start_date": str,
                    "end_date": str
                },
                "strategy": {
                    "exclude_conditions": List[str],
                    "score_factors": List[str],
                    "weights": List[float],
                    "hold_num": int,
                    "stop_profit": float,
                    "fee_rate": float
                }
            }
        
        Returns:
            Dict[str, float]: 回测指标
        """
        try:
            result = self.single_runner.run(
                start_date=config['data']['start_date'],
                end_date=config['data']['end_date'],
                strategy=config['strategy']
            )
            return result['metrics']
            
        except Exception as e:
            logger.error(f"回测执行错误: {str(e)}")
            raise e
    
    def run_batch(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        运行批量回测
        
        Args:
            config: 配置字典，格式如下：
            {
                "data": {
                    "start_date": str,
                    "end_date": str
                },
                "strategies": List[Dict],
                "output_path": Optional[str]
            }
        
        Returns:
            List[Dict[str, Any]]: 回测结果列表
        """
        try:
            return self.batch_runner.run_batch(
                start_date=config['data']['start_date'],
                end_date=config['data']['end_date'],
                strategies=config['strategies'],
                output_path=config.get('output_path')
            )
            
        except Exception as e:
            logger.error(f"批量回测执行错误: {str(e)}")
            raise e 