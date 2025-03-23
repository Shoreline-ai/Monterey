# batch.py - 批量回测模块

import pandas as pd
from cb_backtest.backtester import CBBacktester

class BatchRunner:
    def __init__(self, df: pd.DataFrame, index_df: pd.DataFrame):
        self.df = df
        self.index_df = index_df

    def run_all(self, config_list: list, output_excel_path: str):
        all_results = {}
        for i, cfg in enumerate(config_list):
            print(f"Running backtest {i+1}/{len(config_list)}...")
            tester = CBBacktester(
                df=self.df,
                index_df=self.index_df,
                exclude_conditions=cfg['exclude_conditions'],
                score_factors=cfg['score_factors'],
                weights=cfg['weights'],
                hold_num=cfg.get('hold_num', 5),
                stop_profit=cfg.get('stop_profit', 0.03),
                fee_rate=cfg.get('fee_rate', 0.002)
            )
            result = tester.run()
            all_results[f"run_{i+1}"] = result

        with pd.ExcelWriter(output_excel_path) as writer:
            for name, result in all_results.items():
                result.to_excel(writer, sheet_name=name)

        print(f"✅ All results written to {output_excel_path}")
        return all_results
