import pandas as pd
from pandas import read_excel
import numpy as np
import pandas as pd
pd.options.mode.chained_assignment = None
from datetime import date, datetime, timedelta, timezone
import copy
from pandas import IndexSlice as idx
pd.set_option('display.max_columns', None)  # 当列太多时不换行
from numpy import exp, nan
import quantstats as qs

# import akshare as ak



import warnings
warnings.filterwarnings('ignore') # 忽略警告
import pandas as pd
from pandas import IndexSlice as idx

import talib as ta
# 计算natr
def natr(df, n):
    high = np.array([float(x) for x in df['high']])
    low = np.array([float(x) for x in df['low']])
    close = np.array([float(x) for x in df['close']])
    df['natr'] = ta.NATR(high, low, close, timeperiod=n)
    return df['natr']

pd.set_option('display.max_columns', None)  # 当列太多时不换行
# df = pd.read_pickle('cb_data.pq') # 导入转债数据
# index = pd.read_pickle('index.pq') # 导入指数数据
df = pd.read_parquet('/Users/yiwei/Desktop/git/cb_data.pq') # 导入转债数据
index = pd.read_parquet('/Users/yiwei/Desktop/git/index.pq') # 导入指数数据


# 基础设置
start_date = '20220801' # 开始日期
end_date = '20250901' # 结束日期
hold_num = 5 # 持有数量
SP = 0.03 # 盘中止盈条件
c_rate =  2 / 1000 # 买卖一次花费的总佣金和滑点（双边）
benchmark = 'index_jsl' # 选择基准，集思录等权:index_jsl, 沪深300:index_300, 中证1000:index_1000, 国证2000:index_2000

# df['max_value'] = df.groupby('code')['close'].transform('max')

# df['max_value_position'] = df['close']/df['max_value']

df['max_value'] = df.groupby('code')['close'].cummax().shift(1)

df['max_value_position'] = df['close']/df['max_value']
# 排除设置
df = df[(df.index.get_level_values('trade_date') >= start_date) & (df.index.get_level_values('trade_date') <= end_date)] # 选择时间范围内数据
df['filter'] = False # 初始化过滤器
df.loc[df.is_call.isin(['已公告强赎', '公告到期赎回','公告实施强赎', '公告提示强赎', '已满足强赎条件']), 'filter'] = True # 排除赎回状态
# df.loc[df.high > 188, 'filter'] = True # 排除收盘价大于150的标的
df.loc[df.close > 155, 'filter'] = True # 排除收盘价大于150的标的
df.loc[df.close < 102, 'filter'] = True # 排除收盘价小于100的标的

df.loc[df.amount < 1000, 'filter'] = True # 排除新债
df.loc[df.volatility < 0.02, 'filter'] = True # 排除新债
df.loc[df.pct_chg > 0.06, 'filter'] = True # 排除新债
df.loc[df.pct_chg < -0.15, 'filter'] = True # 排除新债
df.loc[df.close_stk < 3, 'filter'] = True # 排除新债
# df.loc[df.bias_5 > 0.3, 'filter'] = True # 排除新债
# df.loc[df.redeem_remain_days < 10, 'filter'] = True # 排除新债
# df.loc[df.conv_prem > 0.5, 'filter'] = True # 排除新债
# df.loc[df.remain_size > 30, 'filter'] = True # 排除新债
# df.loc[df.pct_chg > 0.-15, 'filter'] = True # 排除新债
# df.loc[df.pct_chg_5 > 0.3, 'filter'] = True # 排除新债


df.loc[df.left_years < 0.7, 'filter'] = True # 排除新债
df.loc[df.list_days <= 3, 'filter'] = True # 排除新债


df['zhengfu'] = (df['high'] - df['low'])/df['close']


# 备用，有优化空间，子策略
# df['zhengfu'] = (df['high'] - df['pre_close'])/df['pre_close']

df['natr_1'] = df.groupby('code').apply(natr, n=1).reset_index(level=0, drop=True) #
df['natr_3'] = df.groupby('code').apply(natr, n=3).reset_index(level=0, drop=True) #
df['natr_5'] = df.groupby('code').apply(natr, n=5).reset_index(level=0, drop=True) #
df['natr_10'] = df.groupby('code').apply(natr, n=10).reset_index(level=0, drop=True) #
df['natr_20'] = df.groupby('code').apply(natr, n=20).reset_index(level=0, drop=True) #


df['zhengfu_cha'] = (df['high'] - df['close'])/(df['open'] - df['close']).abs()


# df['zhengfu'] = (df['high'] - df['low'])/df['low']

# w1: 当天的数据对应的隔天的最大的值对应于今天的close的波动最大
code_group1 = df.groupby('code')
# (2)次日止盈条件

df['aft_high1'] = code_group1.high.shift(-1) # 计算次日最高价
df['aft_high_cur_close'] = (df['aft_high1']-df['close'])/df['close'] # 开盘满足止盈条件则按开盘价计算涨幅



df['turnover_pct'] = df.groupby('trade_date')['turnover'].rank(pct=True) # 将收盘从小到大百分比排列

df['cap_float_share_rate'] = df['remain_cap'] * 10000 /( df['float_share'] * df['close_stk'])

df['zhengfu'] = (df['high'] - df['low'])/df['close']


# df['max_value'] = df.groupby('code')['close'].transform('max')
# df['max_value'] = df.groupby('code')['close'].cummax().shift(1)

# df['max_value_position'] = df['close']/df['max_value']


df['tmp'] = df['pct_chg'] + 1
df['pct_chg_5'] = df.groupby('code')['tmp'].rolling(5, min_periods =1).apply(np.prod, raw = True).reset_index(level=0, drop=True) -1
del df['tmp']





df['tmp2'] = df['pct_chg_stk'] + 1
df['pct_chg_stk_5'] = df.groupby('code')['tmp2'].rolling(5, min_periods =1).apply(np.prod, raw = True).reset_index(level=0, drop=True) -1
del df['tmp2']

# df.loc[df.pct_chg_stk_5 > 0.4, 'is_red'] = 1


# df['is_red_5'] = df.groupby('code')['is_red'].rolling(1, min_periods =1).sum().reset_index(level=0, drop=True)

# df.loc[df.is_red_5 >= 1, 'filter'] = True

# df['max_value'] = df.groupby('code')['close'].cummax().shift(1)

# df['max_value_position'] = df['close']/df['max_value']

df['tmp'] = df['pct_chg'] + 1
df['pct_chg_20'] = df.groupby('code')['tmp'].rolling(20, min_periods =1).apply(np.prod, raw = True).reset_index(level=0, drop=True) -1
del df['tmp']



df['tmp2'] = df['pct_chg_stk'] + 1
df['pct_chg_stk_20'] = df.groupby('code')['tmp2'].rolling(20, min_periods =1).apply(np.prod, raw = True).reset_index(level=0, drop=True) -1
del df['tmp2']

df['turnover_5_avg'] = df.groupby('code')['turnover'].rolling(window=5).mean().reset_index(level=0, drop=True)
df['turnover_10_avg'] = df.groupby('code')['turnover'].rolling(window=10).mean().reset_index(level=0, drop=True)
df['turnover_20_avg'] = df.groupby('code')['turnover'].rolling(window=20).mean().reset_index(level=0, drop=True)
df['turnover_60_avg'] = df.groupby('code')['turnover'].rolling(window=60).mean().reset_index(level=0, drop=True)



df['rolling_1_avg'] = df.groupby('code')['turnover_pct'].rolling(window=1).mean().reset_index(level=0, drop=True)
df['rolling_5_avg'] = df.groupby('code')['turnover_pct'].rolling(window=5).mean().reset_index(level=0, drop=True)
df['rolling_20_avg'] = df.groupby('code')['turnover_pct'].rolling(window=20).mean().reset_index(level=0, drop=True)
df['rolling_50_avg'] = df.groupby('code')['turnover_pct'].rolling(window=50).mean().reset_index(level=0, drop=True)

df['rolling_1_to_5_avg'] = df['rolling_1_avg']/df['rolling_5_avg']
df['rolling_5_to_20_avg'] = df['rolling_5_avg']/df['rolling_20_avg']
df['rolling_20_to_50_avg'] = df['rolling_20_avg']/df['rolling_50_avg']

df['turnover_pct_5_avg'] = df.groupby('code')['turnover_pct'].rolling(window=5).mean().reset_index(level=0, drop=True)


df['bodong_60'] = df.groupby('code').pct_chg_stk.rolling(60).std().reset_index(level=0, drop=True)
df['bodong_60'] = df['bodong_60'] * (60 ** 0.5)

df['bodong_20'] = df.groupby('code').pct_chg_stk.rolling(20).std().reset_index(level=0, drop=True)
df['bodong_20'] = df['bodong_20'] * (20 ** 0.5)


df['bodong_20_to_bodong_60'] = df['bodong_20']/df['bodong_60']

df['bodong_20_bd'] = df.groupby('code').pct_chg.rolling(20).std().reset_index(level=0, drop=True)
df['bodong_20_bd'] = df['bodong_20_bd'] * (20 ** 0.5)



df['bodong_10'] = df.groupby('code').pct_chg_stk.rolling(10).std().reset_index(level=0, drop=True)
df['bodong_10'] = df['bodong_10'] * (10 ** 0.5)


df['bodong_10_bd'] = df.groupby('code').pct_chg.rolling(10).std().reset_index(level=0, drop=True)
df['bodong_10_bd'] = df['bodong_10_bd'] * (10 ** 0.5)

df['bodong_5_bd'] = df.groupby('code').pct_chg.rolling(5).std().reset_index(level=0, drop=True)
df['bodong_5_bd'] = df['bodong_5_bd'] * (5 ** 0.5)



df['zhengfu_1'] = df.groupby('code').zhengfu.rolling(1).std().reset_index(level=0, drop=True)
df['zhengfu_5'] = df.groupby('code').zhengfu.rolling(5).std().reset_index(level=0, drop=True)
df['zhengfu_10'] = df.groupby('code').zhengfu.rolling(10).std().reset_index(level=0, drop=True)
df['zhengfu_20'] = df.groupby('code').zhengfu.rolling(20).std().reset_index(level=0, drop=True)
df['zhengfu_60'] = df.groupby('code').zhengfu.rolling(60).std().reset_index(level=0, drop=True)


df['zhengfu_1_bodong'] = df['zhengfu_1'] * (1 ** 0.5)
df['zhengfu_5_bodong'] = df['zhengfu_5'] * (5 ** 0.5)
df['zhengfu_10_bodong'] = df['zhengfu_10'] * (10 ** 0.5)
df['zhengfu_20_bodong'] = df['zhengfu_20'] * (20 ** 0.5)
df['zhengfu_60_bodong'] = df['zhengfu_60'] * (60 ** 0.5)



# Calculate the conditions
df['high_jump'] = (df['high'] / df['pre_close'] - 1) > 0.025
df['close_drop'] = (df['close'] / df['pre_close'] - 1) < -0.02

# Apply rolling count for past 100 days within each 'code'
df['high_jump_count_100'] = df.groupby('code')['high_jump'].rolling(window=100, min_periods=1).sum().reset_index(0, drop=True)
df['close_drop_count_100'] = df.groupby('code')['close_drop'].rolling(window=100, min_periods=1).sum().reset_index(0, drop=True)

# Apply rolling count for past 100 days within each 'code'
df['high_jump_count_250'] = df.groupby('code')['high_jump'].rolling(window=250, min_periods=1).sum().reset_index(0, drop=True)
df['close_drop_count_250'] = df.groupby('code')['close_drop'].rolling(window=250, min_periods=1).sum().reset_index(0, drop=True)



df['high_jump_count_100_pct'] = df.groupby('trade_date')['high_jump_count_100'].rank(pct=True) # 将收盘从小到大百分比排列
df.loc[df.high_jump_count_100_pct < 0.1, 'filter'] = True # 排除收盘价高于95%的标的
df['high_jump_count_250_pct'] = df.groupby('trade_date')['high_jump_count_250'].rank(pct=True) # 将收盘从小到大百分比排列
df.loc[df.high_jump_count_250_pct < 0.1, 'filter'] = True # 排除收盘价高于95%的标的

df['zhengfu_5'] = df.groupby('code').zhengfu.rolling(5).std().reset_index(level=0, drop=True)
df['zhengfu_10'] = df.groupby('code').zhengfu.rolling(10).std().reset_index(level=0, drop=True)
df['zhengfu_20'] = df.groupby('code').zhengfu.rolling(20).std().reset_index(level=0, drop=True)
df['zhengfu_60'] = df.groupby('code').zhengfu.rolling(60).std().reset_index(level=0, drop=True)


df['zhengfu_5_bodong'] = df['zhengfu_5'] * (5 ** 0.5)
df['zhengfu_10_bodong'] = df['zhengfu_10'] * (10 ** 0.5)
df['zhengfu_20_bodong'] = df['zhengfu_20'] * (20 ** 0.5)
df['zhengfu_60_bodong'] = df['zhengfu_60'] * (60 ** 0.5)



df['close_score'] = df.loc[df['filter'] == False, 'close'].groupby('trade_date').rank(ascending=False)
df['conv_prem_score'] = df.loc[df['filter'] == False, 'conv_prem'].groupby('trade_date').rank(ascending=False)
df['remain_size_score'] = df.loc[df['filter'] == False, 'remain_size'].groupby('trade_date').rank(ascending=False)
df['cap_mv_rate_score'] = df.loc[df['filter'] == False, 'cap_mv_rate'].groupby('trade_date').rank(ascending=False)
df['theory_bias_score'] = df.loc[df['filter'] == False, 'theory_bias'].groupby('trade_date').rank(ascending=False)
df['vol_stk_score'] = df.loc[df['filter'] == False, 'vol_stk'].groupby('trade_date').rank(ascending=False)
df['vol_5_score'] = df.loc[df['filter'] == False, 'vol_5'].groupby('trade_date').rank(ascending=False)
df['bias_5_score'] = df.loc[df['filter'] == False, 'bias_5'].groupby('trade_date').rank(ascending=False)
df['turnover_5_score'] = df.loc[df['filter'] == False, 'turnover_5'].groupby('trade_date').rank(ascending=False)
df['turnover_score'] = df.loc[df['filter'] == False, 'turnover'].groupby('trade_date').rank(ascending=False)
df['max_value_position_score'] = df.loc[df['filter'] == False, 'max_value_position'].groupby('trade_date').rank(ascending=False)
df['high_jump_count_100_score'] = df.loc[df['filter'] == False, 'high_jump_count_100'].groupby('trade_date').rank(ascending=False)
df['close_drop_count_100_score'] = df.loc[df['filter'] == False, 'close_drop_count_100'].groupby('trade_date').rank(ascending=False)
df['high_jump_count_250_score'] = df.loc[df['filter'] == False, 'high_jump_count_250'].groupby('trade_date').rank(ascending=False)
df['close_drop_count_250_score'] = df.loc[df['filter'] == False, 'close_drop_count_250'].groupby('trade_date').rank(ascending=False)
df['bond_prem_score'] = df.loc[df['filter'] == False, 'bond_prem'].groupby('trade_date').rank(ascending=False)
df['ytm_score'] = df.loc[df['filter'] == False, 'ytm'].groupby('trade_date').rank(ascending=False)
df['theory_bias_score'] = df.loc[df['filter'] == False, 'theory_bias'].groupby('trade_date').rank(ascending=False)
df['mod_conv_prem_score'] = df.loc[df['filter'] == False, 'mod_conv_prem'].groupby('trade_date').rank(ascending=False)
df['natr_1_score'] = df.loc[df['filter'] == False, 'natr_1'].groupby('trade_date').rank(ascending=False)
df['natr_3_score'] = df.loc[df['filter'] == False, 'natr_3'].groupby('trade_date').rank(ascending=False)
df['natr_5_score'] = df.loc[df['filter'] == False, 'natr_5'].groupby('trade_date').rank(ascending=False)
df['natr_10_score'] = df.loc[df['filter'] == False, 'natr_10'].groupby('trade_date').rank(ascending=False)
df['natr_20_score'] = df.loc[df['filter'] == False, 'natr_20'].groupby('trade_date').rank(ascending=False)

df['zhengfu_5_bodong_score'] = df.loc[df['filter'] == False, 'zhengfu_5_bodong'].groupby('trade_date').rank(ascending=False)
df['zhengfu_10_bodong_score'] = df.loc[df['filter'] == False, 'zhengfu_10_bodong'].groupby('trade_date').rank(ascending=False)
df['zhengfu_20_bodong_score'] = df.loc[df['filter'] == False, 'zhengfu_20_bodong'].groupby('trade_date').rank(ascending=False)
df['zhengfu_60_bodong_score'] = df.loc[df['filter'] == False, 'zhengfu_60_bodong'].groupby('trade_date').rank(ascending=False)
df['max_value_position_score'] = df.loc[df['filter'] == False, 'max_value_position'].groupby('trade_date').rank(ascending=False)


df['alpha_pct_chg_5_score'] = df.loc[df['filter'] == False, 'alpha_pct_chg_5'].groupby('trade_date').rank(ascending=False)
df['conv_prem_score'] = df.loc[df['filter'] == False, 'conv_prem'].groupby('trade_date').rank(ascending=False)

# df['score'] = df.SDZ + df.max_value_position_score * -0.5
# df['score'] = df['close_score'] * 1 + df['conv_prem_score'] * -1 + df['remain_size_score'] * -1
# df['score'] =df['alpha_pct_chg_5_score'] * -10 +  df['cap_mv_rate_score'] * -10 + df['vol_stk_score'] * 10 + df['conv_prem_score'] * -10  + df['max_value_position'] * -10


# df['score'] =df['alpha_pct_chg_5_score'] * -10 +  df['cap_mv_rate_score'] * -10 + df['vol_stk_score'] * 10 + df['conv_prem_score'] * -10 
# + df['max_value_position'] * -10 + df['high_jump_count_100_score'] * 10 + df['close_drop_count_100_score'] * -10

# df['score'] = df['bond_prem_score'] * -10 + df['ytm_score'] * 10 + df['theory_bias_score'] * -10 + df['cap_mv_rate_score'] * -10 + df['turnover_5_score'] * 15
df['score'] = df['bond_prem_score'] * -10 + df['ytm_score'] * 10 + df['theory_bias_score'] * -10 + df['cap_mv_rate_score'] * -10 + df['turnover_5_score'] * 15 + + df.max_value_position_score * 0

# df['score'] =df['cap_mv_rate_score'] * -10 +  df['mod_conv_prem_score'] * -10 + df['ytm_score'] * 10 
# df['score'] = df.dblow * -1 + df.conv_prem_score * -1 + df.natr_5_score * 0.5 + df.turnover_5_score* 0.5 + df.theory_bias_score * -0.5 + df.bond_prem_score * -1 + df.zhengfu_5_bodong_score * 0.5 + + df.max_value_position_score * -2

# 溢价 0.5，价格 155，止盈 5 100% 年华
# 溢价 1，价格 155，止盈 5 13% 回撤
# df['score'] =  df.natr_5_score * 5 + df.turnover_5_score* 0.5 + df.theory_bias_score * -0.5 + df.bond_prem_score * -1 + df.zhengfu_5_bodong_score * 0.5 + df.max_value_position_score * -2
# df['score'] =  df.natr_5_score * 5 + df.turnover_5_score* 0.5 + df.theory_bias_score * -0.5 + df.bond_prem_score * -1 + df.zhengfu_5_bodong_score * 0.5




df['rank'] = df.groupby('trade_date')['score'].rank('first', ascending=True) # 按总分从高到低计算排名


code_group = df.groupby('code')
# (2)次日止盈条件
df['aft_open'] = code_group.open.shift(-1) # 计算次日开盘价
df['aft_close'] = code_group.close.shift(-1) # 计算次日收盘价
df['aft_high'] = code_group.high.shift(-1) # 计算次日最高价
df['time_return']= code_group.pct_chg.shift(-1) # 先计算不止盈情况的收益率
df['SFZY']='未满足止盈' #先记录默认情况
pd.set_option('display.max_columns', None)  # 当列太多时不换行

df.loc[df['aft_high'] >= df['close'] * (1+SP),'time_return'] = SP # 满足止盈条件止盈
df.loc[df['aft_open'] >= df['close'] * (1+SP),'time_return'] = \
(df['aft_open']-df['close'])/df['close'] # 开盘满足止盈条件则按开盘价计算涨幅
df.loc[df['aft_high'] >= df['close'] * (1+SP),'SFZY'] = '满足止盈'

# 计算每日信号 采样信号 持仓状态
df.loc[(df['rank'] <= hold_num), 'signal'] = 1 # 标记信号
df.dropna(subset=['signal'], inplace=True) # 删除没有标记的行
df.sort_values(by='trade_date', inplace=True) # 按日期排序

res = pd.DataFrame()
res['time_return'] = df.groupby('trade_date')['time_return'].mean() # 按等权计算组合回报
pd.set_option('display.max_rows',None)
# 计算手续费
pos_df = df['signal'].unstack('code')
pos_df.fillna(0, inplace=True)
res['cost'] = pos_df.diff().abs().sum(axis=1) * c_rate / (pos_df.shift().sum(axis=1) + pos_df.sum(axis=1))
res.iloc[0, 1] = 0.5 * c_rate# 修正首行手续费
res['time_return'] = (res['time_return'] + 1) * (1 - res['cost']) - 1# 扣除手续费及佣金后的回报

# 确保数据格式正确
clean_returns = res.time_return.astype(float)
if not isinstance(clean_returns.index, pd.DatetimeIndex):
    clean_returns.index = pd.to_datetime(clean_returns.index)
clean_returns = clean_returns.sort_index()

# 处理基准数据
clean_benchmark = None
if benchmark is not None:
    clean_benchmark = index[benchmark].astype(float)
    if not isinstance(clean_benchmark.index, pd.DatetimeIndex):
        clean_benchmark.index = pd.to_datetime(clean_benchmark.index)
    clean_benchmark = clean_benchmark.sort_index()
    
    # 对齐数据
    clean_benchmark = clean_benchmark.reindex(clean_returns.index)

# 使用 resample 预处理数据
if clean_returns.index.duplicated().any():
    clean_returns = clean_returns.resample('D').last()
if clean_benchmark is not None and clean_benchmark.index.duplicated().any():
    clean_benchmark = clean_benchmark.resample('D').last()

# 生成报告
from .utils import generate_qs_report

generate_qs_report(
    returns=res.time_return,
    benchmark=index[benchmark] if benchmark else None,
    title="Strategy Performance Report",
    periods_per_year=252
)