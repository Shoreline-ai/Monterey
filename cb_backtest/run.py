# run.py - 主入口脚本

import os
import json
import argparse
import pandas as pd
from engine import FactorEngine
from batch import BatchRunner
from eval import evaluate_performance

def load_config(config_path):
    with open(config_path, 'r') as f:
        return json.load(f)

def main(config_path):
    config = load_config(config_path)

    # 1. 读取数据
    df = pd.read_parquet(config['data']['cb_data_path'])
    index_df = pd.read_parquet(config['data']['index_data_path'])
    start_date = config['data'].get('start_date')
    end_date = config['data'].get('end_date')

    df = df.loc[(df.index.get_level_values('trade_date') >= start_date) &
                    (df.index.get_level_values('trade_date') <= end_date)].copy()

    index_df = index_df.loc[(index_df.index >= start_date) & (index_df.index <= end_date)].copy()


    # 2. 计算因子
    engine = FactorEngine(df)
    df_with_factors = engine.compute_all_factors()

    # 3. 初始化过滤字段（打分前会用到）
    df_with_factors['filter'] = False

    # 4. 批量执行回测
    runner = BatchRunner(df_with_factors, index_df)
    results = runner.run_all(config['strategies'], output_excel_path=config['output_path'])

    # 5. 绩效评估输出
    print("\n=== Performance Summary ===")
    for name, result_df in results.items():
        metrics = evaluate_performance(result_df)
        print(f"{name}: {metrics}")

if __name__ == '__main__':
    print("开始运行回测")
    parser = argparse.ArgumentParser(description='Run convertible bond backtest.')
    parser.add_argument('--config', type=str, default='cb_backtest/config/config.json', help='Path to JSON config file')
    args = parser.parse_args()

    main(args.config)