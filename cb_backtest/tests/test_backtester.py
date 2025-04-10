import unittest
import pandas as pd
import numpy as np
from ..core.backtester import CBBacktester

class TestCBBacktester(unittest.TestCase):
    def setUp(self):
        """准备测试数据"""
        # 创建测试用的MultiIndex DataFrame
        dates = ['20240101', '20240102', '20240103']
        codes = ['123001', '123002', '123003']
        
        # 创建MultiIndex
        index = pd.MultiIndex.from_product(
            [codes, dates],
            names=['code', 'trade_date']
        )
        
        # 创建测试数据
        data = {
            'close': np.random.uniform(100, 150, len(index)),
            'open': np.random.uniform(100, 150, len(index)),
            'high': np.random.uniform(100, 150, len(index)),
            'low': np.random.uniform(100, 150, len(index)),
            'pct_chg': np.random.uniform(-0.05, 0.05, len(index)),
            'amount': np.random.uniform(1000, 5000, len(index)),
            'is_call': ['正常'] * len(index),
            'bond_prem': np.random.uniform(-0.1, 0.1, len(index)),
            'ytm': np.random.uniform(0, 0.05, len(index)),
            'turnover_5': np.random.uniform(0, 0.2, len(index)),
            'left_years': np.random.uniform(1, 5, len(index))
        }
        
        self.df = pd.DataFrame(data, index=index)
        self.index_df = pd.DataFrame(index=dates)  # 简单的指数数据
        
        # 设置测试参数
        self.exclude_conditions = [
            "close < 102",
            "close > 155",
            "left_years < 0.7",
            "amount < 1000"
        ]
        self.score_factors = [
            "bond_prem",
            "ytm",
            "turnover_5"
        ]
        self.weights = [-10, 10, 5]
        self.hold_num = 2
        self.stop_profit = 0.03
        self.fee_rate = 0.002

    def test_init(self):
        """测试初始化"""
        backtester = CBBacktester(
            df=self.df,
            index_df=self.index_df,
            exclude_conditions=self.exclude_conditions,
            score_factors=self.score_factors,
            weights=self.weights,
            hold_num=self.hold_num,
            stop_profit=self.stop_profit,
            fee_rate=self.fee_rate
        )
        
        self.assertIsNotNone(backtester)
        self.assertEqual(backtester.hold_num, self.hold_num)
        self.assertEqual(backtester.SP, self.stop_profit)
        self.assertEqual(backtester.c_rate, self.fee_rate)

    def test_apply_filters(self):
        """测试过滤条件应用"""
        backtester = CBBacktester(
            df=self.df,
            index_df=self.index_df,
            exclude_conditions=self.exclude_conditions,
            score_factors=self.score_factors,
            weights=self.weights,
            hold_num=self.hold_num
        )
        
        backtester.apply_filters()
        self.assertIn('filter', backtester.df.columns)
        
        # 验证过滤条件是否正确应用
        filtered_data = backtester.df[~backtester.df['filter']]
        self.assertTrue(all(filtered_data['close'] >= 102))
        self.assertTrue(all(filtered_data['close'] <= 155))
        self.assertTrue(all(filtered_data['left_years'] >= 0.7))
        self.assertTrue(all(filtered_data['amount'] >= 1000))

    def test_compute_score(self):
        """测试评分计算"""
        backtester = CBBacktester(
            df=self.df,
            index_df=self.index_df,
            exclude_conditions=self.exclude_conditions,
            score_factors=self.score_factors,
            weights=self.weights,
            hold_num=self.hold_num
        )
        
        backtester.apply_filters()
        backtester.compute_score()
        
        self.assertIn('score', backtester.df.columns)
        self.assertIn('rank', backtester.df.columns)
        
        # 验证每个交易日的排名
        for date in self.df.index.get_level_values('trade_date').unique():
            date_data = backtester.df.xs(date, level='trade_date')
            date_ranks = date_data[~date_data['filter']]['rank']
            
            # 验证排名的范围
            if not date_ranks.empty:
                self.assertTrue(all(date_ranks >= 1))
                self.assertTrue(all(date_ranks <= len(date_ranks)))
                
                # 验证排名的连续性
                expected_ranks = set(range(1, len(date_ranks) + 1))
                actual_ranks = set(date_ranks)
                self.assertEqual(expected_ranks, actual_ranks)

    def test_simulate(self):
        """测试交易模拟"""
        backtester = CBBacktester(
            df=self.df,
            index_df=self.index_df,
            exclude_conditions=self.exclude_conditions,
            score_factors=self.score_factors,
            weights=self.weights,
            hold_num=self.hold_num
        )
        
        results = backtester.run()
        
        self.assertIsNotNone(results)
        self.assertIn('time_return', results.columns)
        self.assertIn('cost', results.columns)
        
        # 验证结果的基本属性
        self.assertTrue(isinstance(results.index, pd.DatetimeIndex))
        self.assertTrue(all(results['cost'] >= 0))
        self.assertTrue(all(results['cost'] <= self.fee_rate * 2))  # 最大成本不超过双倍费率

    def test_full_backtest(self):
        """测试完整的回测流程"""
        backtester = CBBacktester(
            df=self.df,
            index_df=self.index_df,
            exclude_conditions=self.exclude_conditions,
            score_factors=self.score_factors,
            weights=self.weights,
            hold_num=self.hold_num
        )
        
        results = backtester.run()
        
        # 验证结果的完整性
        self.assertIsNotNone(results)
        self.assertTrue(len(results) > 0)
        
        # 验证结果长度（考虑到最后一天没有next day return）
        unique_dates = self.df.index.get_level_values('trade_date').unique()
        expected_length = len(unique_dates) - 1
        self.assertEqual(len(results), expected_length)
        
        # 验证日期范围
        start_date = pd.to_datetime(unique_dates[0])
        end_date = pd.to_datetime(unique_dates[-2])  # 最后一天没有next day return
        self.assertEqual(results.index[0], start_date)
        self.assertEqual(results.index[-1], end_date)

if __name__ == '__main__':
    unittest.main() 