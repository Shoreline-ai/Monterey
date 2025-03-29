# engine.py - 因子计算模块

import pandas as pd
import numpy as np
import talib as ta

class FactorEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def compute_all_factors(self) -> pd.DataFrame:
        df = self.df

        # 创建过滤条件
        df['filter'] = False  # 默认不过滤任何数据
        
        # 计算各种因子
        df['max_value'] = df.groupby('code')['close'].cummax().shift(1)
        df['max_value_position'] = df['close'] / df['max_value']

        df['zhengfu'] = (df['high'] - df['low']) / df['close']
        df['tmp'] = df['pct_chg'] + 1
        df['pct_chg_5'] = df.groupby('code')['tmp'].rolling(5, min_periods=1).apply(np.prod, raw=True).reset_index(level=0, drop=True) - 1
        df.drop(columns='tmp', inplace=True)

        df['tmp2'] = df['pct_chg_stk'] + 1
        df['pct_chg_stk_5'] = df.groupby('code')['tmp2'].rolling(5, min_periods=1).apply(np.prod, raw=True).reset_index(level=0, drop=True) - 1
        df.drop(columns='tmp2', inplace=True)

        df['turnover_5_avg'] = df.groupby('code')['turnover'].rolling(window=5).mean().reset_index(level=0, drop=True)
        df['rolling_5_avg'] = df.groupby('code')['turnover'].rank(pct=True)

        # NATR计算
        def natr(sub_df, n):
            return ta.NATR(
                sub_df['high'].values,
                sub_df['low'].values,
                sub_df['close'].values,
                timeperiod=n
            )

        for n in [1, 3, 5, 10, 20]:
            df[f'natr_{n}'] = df.groupby('code').apply(lambda x: pd.Series(natr(x, n), index=x.index)).reset_index(level=0, drop=True)

        # # 应用排除条件（从配置文件中读取）
        # # 这里添加了一些常见的排除条件作为示例
        # df.loc[df['close'] > 155, 'filter'] = True  # 价格过高的转债
        # df.loc[df['left_years'] < 0.7, 'filter'] = True  # 剩余期限过短的转债

        # score_fields = [
        #     'max_value_position', 'turnover_5_avg', 'pct_chg_5', 'pct_chg_stk_5',
        #     'natr_1', 'natr_3', 'natr_5', 'natr_10', 'natr_20'
        # ]
        # for field in score_fields:
        #     score_name = f"{field}_score"
        #     df[score_name] = df.loc[df['filter'] == False, field].groupby('trade_date').rank(ascending=False)

        self.df = df
        return df
