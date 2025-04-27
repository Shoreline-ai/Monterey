# backtester.py - 回测模块

import pandas as pd
import numpy as np
import logging
from .engine import FactorEngine

logger = logging.getLogger(__name__)

class CBBacktester:
    def __init__(self, df, index_df, exclude_conditions=None, score_factors=None, weights=None, hold_num=5, stop_profit=0.03, fee_rate=0.002):
        """
        初始化回测器
        
        Args:
            df (pd.DataFrame): MultiIndex DataFrame，包含 code 和 trade_date 两级索引
            index_df (pd.DataFrame): 指数数据
            exclude_conditions (list): 排除条件列表
            score_factors (list): 评分因子列表
            weights (list): 因子权重列表
            hold_num (int): 持仓数量
            stop_profit (float): 止盈比例
            fee_rate (float): 交易费率
        """
        if not isinstance(df.index, pd.MultiIndex):
            raise ValueError("df must have MultiIndex with levels ['code', 'trade_date']")
            
        if not all(level in df.index.names for level in ['code', 'trade_date']):
            raise ValueError("df must have 'code' and 'trade_date' as index levels")
            
        self.df = df.copy()
        self.index_df = index_df
        self.exclude_conditions = exclude_conditions or []
        self.score_factors = score_factors or []
        self.weights = weights or []
        self.hold_num = hold_num
        self.SP = stop_profit
        self.c_rate = fee_rate
        
        # 初始化过滤列
        self.df['filter'] = False
        
        logger.info(f"Initialized CBBacktester with {len(self.df)} records")
        logger.info(f"Index levels: {self.df.index.names}")
        logger.info(f"Available columns: {self.df.columns.tolist()}")
        
    def apply_filters(self):
        """应用过滤条件"""
        logger.info("Applying filters...")
        
        # 重置过滤标记
        self.df['filter'] = False
        
        for condition in self.exclude_conditions:
            try:
                mask = self.df.eval(condition)
                self.df.loc[mask, 'filter'] = True
                logger.debug(f"Applied filter: {condition}, excluded {mask.sum()} records")
            except Exception as e:
                logger.error(f"Error applying filter '{condition}': {str(e)}")
                raise
                
        total_filtered = self.df['filter'].sum()
        logger.info(f"Total filtered records: {total_filtered}")
        
    def compute_score(self):
        """计算评分并排名"""
        logger.info("Computing scores...")
        
        if not self.score_factors or not self.weights:
            logger.warning("No score factors or weights provided")
            return
            
        try:
            # 初始化得分
            self.df['score'] = 0
            
            # 计算每个因子的得分
            for factor, weight in zip(self.score_factors, self.weights):
                if factor not in self.df.columns:
                    raise ValueError(f"Factor {factor} not found in DataFrame")
                    
                self.df['score'] += self.df[factor] * weight
                
            # 对每个交易日分别排名
            self.df['rank'] = np.nan
            
            for date in self.df.index.get_level_values('trade_date').unique():
                # 获取当日未被过滤的数据
                mask = (self.df.index.get_level_values('trade_date') == date) & (~self.df['filter'])
                valid_data = self.df.loc[mask]
                
                if not valid_data.empty:
                    # 计算排名（升序，1为最好）
                    ranks = valid_data['score'].rank(method='min', ascending=True)
                    self.df.loc[mask, 'rank'] = ranks
                    
            logger.info("Score computation completed")
            
        except Exception as e:
            logger.error(f"Error in compute_score: {str(e)}")
            raise
            
    def simulate(self):
        """模拟交易"""
        logger.info("Starting trade simulation...")
        
        try:
            # 获取所有交易日期
            dates = sorted(self.df.index.get_level_values('trade_date').unique())
            
            # 初始化结果DataFrame
            results = pd.DataFrame(index=pd.to_datetime(dates[:-1]))  # 最后一天没有next day return
            results['time_return'] = 0.0
            results['cost'] = 0.0
            
            # 对每个交易日进行模拟
            for i in range(len(dates) - 1):
                current_date = dates[i]
                next_date = dates[i+1]
                
                # 获取当前日期的数据
                current_data = self.df.xs(current_date, level='trade_date')
                next_data = self.df.xs(next_date, level='trade_date')
                
                # 获取当日排名前N的转债
                valid_data = current_data[~current_data['filter']]
                selected = valid_data[valid_data['rank'] <= self.hold_num]
                
                if selected.empty:
                    continue
                    
                # 计算收益率
                selected_codes = selected.index.tolist()
                next_day_returns = next_data.loc[selected_codes, 'pct_chg']
                
                # 计算等权重组合收益
                portfolio_return = next_day_returns.mean()
                
                # 记录结果
                results.loc[pd.to_datetime(current_date), 'time_return'] = portfolio_return
                results.loc[pd.to_datetime(current_date), 'cost'] = self.c_rate
                
            logger.info("Trade simulation completed")
            return results
            
        except Exception as e:
            logger.error(f"Error in simulate: {str(e)}")
            raise
            
    def run(self):
        """运行回测"""
        logger.info("Starting backtest...")
        
        try:
            # 应用过滤条件
            self.apply_filters()
            
            # 计算评分
            self.compute_score()
            
            # 模拟交易
            results = self.simulate()
            
            logger.info("Backtest completed successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error in run: {str(e)}")
            raise
