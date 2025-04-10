from typing import Dict, Any
import logging
import pandas as pd
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
        # 读取数据
        self.cb_data = pd.read_parquet(cb_data_path)
        self.index_data = pd.read_parquet(index_data_path)
        
        # 打印数据信息
        logger.info(f"CB Data columns: {self.cb_data.columns.tolist()}")
        logger.info(f"CB Data shape: {self.cb_data.shape}")
        logger.info(f"CB Data date range: {self.cb_data.index.get_level_values('trade_date').min()} to {self.cb_data.index.get_level_values('trade_date').max()}")
        logger.info(f"CB Data unique dates count: {len(self.cb_data.index.get_level_values('trade_date').unique())}")
        logger.info(f"CB Data unique codes count: {len(self.cb_data.index.get_level_values('code').unique())}")
        logger.info(f"CB Data head:\n{self.cb_data.head()}")
        logger.info(f"CB Data dtypes:\n{self.cb_data.dtypes}")
        logger.info(f"CB Data index:\n{self.cb_data.index}")
        
        # 打印指数数据信息
        logger.info(f"Index Data columns: {self.index_data.columns.tolist()}")
        logger.info(f"Index Data head:\n{self.index_data.head()}")
        logger.info(f"Index Data index:\n{self.index_data.index}")
        
        # 确保可转债数据有正确的MultiIndex
        if not isinstance(self.cb_data.index, pd.MultiIndex):
            raise ValueError("CB data must have MultiIndex with (code, trade_date)")
            
        # 如果指数数据不是MultiIndex，将其转换为MultiIndex
        if not isinstance(self.index_data.index, pd.MultiIndex):
            logger.info("Converting index data to MultiIndex format")
            
            # 检查是否已经有trade_date作为索引
            if self.index_data.index.name == 'trade_date':
                logger.info("Index data already has trade_date as index")
                # 重置索引，将trade_date变成列
                self.index_data = self.index_data.reset_index()
            else:
                # 检查日期列的名称
                date_columns = [col for col in self.index_data.columns if 'date' in col.lower()]
                if not date_columns:
                    raise ValueError("No date column found in index data")
                date_column = date_columns[0]
                logger.info(f"Using {date_column} as trade_date column")
                # 重命名日期列
                self.index_data = self.index_data.rename(columns={date_column: 'trade_date'})
            
            # 添加code列并设置MultiIndex
            self.index_data['code'] = '000001.SH'  # 使用上证指数作为默认指数
            self.index_data = self.index_data.set_index(['code', 'trade_date'])
            logger.info(f"Index Data after conversion:\n{self.index_data.head()}")
        
        # 确保必要的列存在
        required_columns = ['close', 'open', 'high', 'low', 'pct_chg']  # trade_date和code在索引中
        missing_columns = [col for col in required_columns if col not in self.cb_data.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in cb_data: {missing_columns}")
        
        # 确保索引中的trade_date是字符串类型，格式为YYYYMMDD
        self.cb_data.index = self.cb_data.index.set_levels(
            [self.cb_data.index.levels[0],  # code level
             pd.to_datetime(self.cb_data.index.levels[1]).strftime('%Y%m%d')]  # trade_date level
        )
        
        # 将指数数据的日期转换为字符串类型，格式为YYYYMMDD
        if isinstance(self.index_data.index, pd.MultiIndex):
            self.index_data.index = self.index_data.index.set_levels(
                [self.index_data.index.levels[0],  # code level
                pd.to_datetime(self.index_data.index.levels[1]).strftime('%Y%m%d')]  # trade_date level
            )
        
        # 打印转换后的日期范围
        logger.info(f"After format conversion - CB Data date range: {self.cb_data.index.get_level_values('trade_date').min()} to {self.cb_data.index.get_level_values('trade_date').max()}")
        logger.info(f"After format conversion - Index Data date range: {self.index_data.index.get_level_values('trade_date').min()} to {self.index_data.index.get_level_values('trade_date').max()}")
        
        self._engine = None
    
    @property
    def engine(self) -> CBBacktester:
        """懒加载回测引擎"""
        if self._engine is None:
            self._engine = CBBacktester(
                df=self.cb_data,
                index_df=self.index_data,
                exclude_conditions=[],  # 初始化时不设置过滤条件
                score_factors=[],       # 初始化时不设置评分因子
                weights=[],             # 初始化时不设置权重
            )
        return self._engine
    
    def run(self, 
            start_date: str,
            end_date: str,
            strategy: Dict[str, Any]) -> Dict[str, Any]:
        """
        运行单次回测
        
        Args:
            start_date: 开始日期，格式：YYYYMMDD
            end_date: 结束日期，格式：YYYYMMDD
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
            logger.info(f"Running backtest from {start_date} to {end_date}")
            logger.info(f"Strategy: {strategy}")
            
            # 检查数据集的日期范围
            data_start = self.cb_data.index.get_level_values('trade_date').min()
            data_end = self.cb_data.index.get_level_values('trade_date').max()
            
            logger.info(f"Data date range: {data_start} to {data_end}")
            logger.info(f"Request date range: {start_date} to {end_date}")
            
            # 确保日期格式一致进行比较
            start_date = pd.to_datetime(start_date).strftime('%Y%m%d')
            end_date = pd.to_datetime(end_date).strftime('%Y%m%d')
            data_start = pd.to_datetime(data_start).strftime('%Y%m%d')
            data_end = pd.to_datetime(data_end).strftime('%Y%m%d')
            
            if start_date < data_start:
                logger.warning(f"Requested start_date {start_date} is earlier than available data start date {data_start}")
                return {
                    "strategy": strategy,
                    "metrics": {
                        "error": f"Requested start_date {start_date} is earlier than available data start date {data_start}",
                        "final_nav": 1.0,
                        "annual_return": 0.0,
                        "max_drawdown": 0.0,
                        "volatility": 0.0,
                        "sharpe": 0.0,
                        "sortino_ratio": 0.0,
                        "win_rate": 0.0,
                        "trade_count": 0,
                        "avg_hold_days": 0,
                        "total_days": 0,
                        "start_date": None,
                        "end_date": None
                    },
                    "daily_returns": {},
                    "positions": {},
                    "trades": []
                }
            
            if end_date > data_end:
                logger.warning(f"Requested end_date {end_date} is later than available data end date {data_end}, will use {data_end} instead")
                end_date = data_end
            
            # 使用索引级别进行日期过滤
            filtered_data = self.cb_data[
                (self.cb_data.index.get_level_values('trade_date') >= start_date) & 
                (self.cb_data.index.get_level_values('trade_date') <= end_date)
            ].copy()
            
            filtered_index_data = self.index_data[
                (self.index_data.index.get_level_values('trade_date') >= start_date) & 
                (self.index_data.index.get_level_values('trade_date') <= end_date)
            ].copy()
            
            logger.info(f"Filtered data shape: {filtered_data.shape}")
            logger.info(f"Filtered date range: {filtered_data.index.get_level_values('trade_date').min()} to {filtered_data.index.get_level_values('trade_date').max()}")
            logger.info(f"Filtered index data shape: {filtered_index_data.shape}")
            
            if filtered_data.empty:
                logger.warning(f"No data found between {start_date} and {end_date}")
                return {
                    "strategy": strategy,
                    "metrics": {
                        "error": "No data in specified date range",
                        "final_nav": 1.0,
                        "annual_return": 0.0,
                        "max_drawdown": 0.0,
                        "volatility": 0.0,
                        "sharpe": 0.0,
                        "total_days": 0,
                        "start_date": None,
                        "end_date": None
                    }
                }
            
            # 创建新的回测引擎实例
            backtester = CBBacktester(
                df=filtered_data,
                index_df=filtered_index_data,
                exclude_conditions=strategy['exclude_conditions'],
                score_factors=strategy['score_factors'],
                weights=strategy['weights'],
                hold_num=strategy['hold_num'],
                stop_profit=strategy['stop_profit'],
                fee_rate=strategy['fee_rate']
            )
            
            # 运行回测
            results = backtester.run()
            logger.info(f"Backtest results shape: {results.shape if results is not None else 'None'}")
            
            # 评估性能
            metrics = evaluate_performance(results)
            logger.info(f"Performance metrics: {metrics}")
            
            return {
                "strategy": strategy,
                "metrics": {
                    "annual_return": metrics["annual_return"],
                    "max_drawdown": metrics["max_drawdown"],
                    "volatility": metrics["volatility"],
                    "sharpe": metrics["sharpe"],
                    "sortino_ratio": metrics["sortino_ratio"],
                    "win_rate": metrics["win_rate"],
                    "trade_count": metrics["trade_count"],
                    "avg_hold_days": metrics["avg_hold_days"],
                    "start_date": metrics["start_date"],
                    "end_date": metrics["end_date"],
                    "total_days": metrics["total_days"]
                },
                "daily_returns": metrics["daily_returns"],
                "positions": metrics["positions"],
                "trades": metrics["trades"]
            }
            
        except Exception as e:
            logger.error(f"单次回测执行错误: {str(e)}")
            raise e 