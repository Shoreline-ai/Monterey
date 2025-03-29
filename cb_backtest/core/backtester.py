# backtester.py - 回测模块

import pandas as pd
import numpy as np

class CBBacktester:
    def __init__(self, df, index_df, exclude_conditions, score_factors, weights, hold_num=5, stop_profit=0.03, fee_rate=0.002):
        self.df = df.copy()
        self.index_df = index_df
        self.exclude_conditions = exclude_conditions
        self.score_factors = score_factors
        self.weights = weights
        self.hold_num = hold_num
        self.SP = stop_profit
        self.c_rate = fee_rate

    def apply_filters(self):
        self.df['filter'] = False
        self.df.loc[self.df.is_call.isin(['已公告强赎', '公告到期赎回','公告实施强赎', '公告提示强赎', '已满足强赎条件']), 'filter'] = True # 排除赎回状态
        for cond in self.exclude_conditions:
            try:
                self.df.loc[self.df.eval(cond), 'filter'] = True
            except Exception as e:
                print(f"Error evaluating condition '{cond}': {e}")
        
        # 确保每个交易日至少有hold_num个可交易的转债
        date_counts = self.df[~self.df['filter']].groupby('trade_date').size()
        dates_to_unfilter = date_counts[date_counts < self.hold_num].index
        if not dates_to_unfilter.empty:
            print(f"Warning: {len(dates_to_unfilter)} trading days have less than {self.hold_num} bonds available")
            for date in dates_to_unfilter:
                self.df.loc[self.df['trade_date'] == date, 'filter'] = False

    def compute_score(self):
        # 计算综合得分
        self.df['score'] = 0
        for factor, weight in zip(self.score_factors, self.weights):
            # 对每个因子计算排名得分
            self.df[f"{factor}_rank"] = self.df.loc[~self.df['filter'], factor].groupby('trade_date').rank(ascending=False)
            # 将NaN填充为最大值+1（相当于最差排名）
            max_rank = self.df[f"{factor}_rank"].max()
            self.df[f"{factor}_rank"].fillna(max_rank + 1, inplace=True)
            # 将排名加权计入总分
            self.df['score'] += self.df[f"{factor}_rank"] * weight
        
        # 计算最终排名
        self.df['rank'] = self.df.groupby('trade_date')['score'].rank('first', ascending=True)

    def simulate(self):
        code_group = self.df.groupby('code')
        self.df['aft_open'] = code_group.open.shift(-1)
        self.df['aft_high'] = code_group.high.shift(-1)
        self.df['time_return'] = code_group.pct_chg.shift(-1)

        # 处理止盈情况
        self.df.loc[self.df['aft_high'] >= self.df['close'] * (1 + self.SP), 'time_return'] = self.SP
        self.df.loc[self.df['aft_open'] >= self.df['close'] * (1 + self.SP), 'time_return'] = (
            (self.df['aft_open'] - self.df['close']) / self.df['close'])

        # 生成交易信号
        self.df['signal'] = 0
        self.df.loc[(self.df['rank'] <= self.hold_num) & (~self.df['filter']), 'signal'] = 1

        # 计算组合收益
        df_signal = self.df[self.df['signal'] == 1].copy()
        if df_signal.empty:
            print("Warning: No trading signals generated")
            return pd.DataFrame(columns=['time_return', 'cost'])
            
        df_signal.sort_values(by='trade_date', inplace=True)

        # 计算每日收益
        res = pd.DataFrame()
        daily_returns = df_signal.groupby('trade_date')['time_return'].mean()
        res['time_return'] = daily_returns.fillna(0)  # 如果某天没有持仓，收益为0

        # 计算交易成本
        pos_df = df_signal['signal'].unstack('code')
        pos_df.fillna(0, inplace=True)
        
        # 计算换手成本
        position_changes = pos_df.diff().abs().sum(axis=1)
        total_positions = pos_df.shift().sum(axis=1) + pos_df.sum(axis=1)
        res['cost'] = np.where(total_positions > 0,
                             position_changes * self.c_rate / total_positions,
                             0)
        
        # 第一天的成本
        if not res.empty:
            res.iloc[0, res.columns.get_loc('cost')] = 0.5 * self.c_rate

        # 计算考虑成本后的收益
        res['time_return'] = (res['time_return'] + 1) * (1 - res['cost']) - 1

        return res

    def run(self):
        self.apply_filters()
        self.compute_score()
        return self.simulate()
