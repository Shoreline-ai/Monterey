# engine.py - 因子计算模块

import pandas as pd
import numpy as np

class FactorEngine:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def compute_all_factors(self) -> pd.DataFrame:
        df = self.df

        # 创建过滤条件
        df['filter'] = False  # 默认不过滤任何数据
        
        # 计算动量相关因子
        df['max_value'] = df.groupby('code')['close'].cummax().shift(1)
        df['max_value_position'] = df['close'] / df['max_value']
        df['zhengfu'] = (df['high'] - df['low']) / df['close']

        # NATR波动率因子
        def natr(sub_df, n):
            # 计算真实范围 (True Range)
            tr = pd.DataFrame({
                'hl': sub_df['high'] - sub_df['low'],
                'hc': abs(sub_df['high'] - sub_df['close'].shift(1)),
                'lc': abs(sub_df['low'] - sub_df['close'].shift(1))
            }).max(axis=1)
            
            # 计算ATR (Average True Range)
            atr = tr.rolling(window=n).mean()
            
            # 计算NATR (Normalized Average True Range)
            natr = (atr / sub_df['close']) * 100
            return natr

        for n in [1, 3, 5, 10, 20]:
            df[f'natr_{n}'] = df.groupby('code').apply(lambda x: pd.Series(natr(x, n), index=x.index)).reset_index(level=0, drop=True)

        # 动量因子
        df['momentum_20'] = df.groupby('code')['close'].pct_change(20)
        df['momentum_60'] = df.groupby('code')['close'].pct_change(60)

        # 相对强弱因子
        df['rs_5'] = df.groupby('code')['close'].pct_change(5) - df.groupby('trade_date')['close'].transform('mean').pct_change(5)
        df['rs_20'] = df.groupby('code')['close'].pct_change(20) - df.groupby('trade_date')['close'].transform('mean').pct_change(20)

        self.df = df
        return df
