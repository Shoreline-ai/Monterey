from typing import Dict, List, Any, Optional
import logging
import pandas as pd
from pathlib import Path
from .single_runner import SingleRunner

logger = logging.getLogger(__name__)

class BatchRunner:
    """批量回测运行器"""
    
    def __init__(self, cb_data_path: str, index_data_path: str):
        """
        初始化批量回测运行器
        
        Args:
            cb_data_path: 可转债数据文件路径
            index_data_path: 指数数据文件路径
        """
        self.single_runner = SingleRunner(
            cb_data_path=cb_data_path,
            index_data_path=index_data_path
        )
    
    def run_batch(self, 
                 start_date: str,
                 end_date: str,
                 strategies: List[Dict[str, Any]],
                 output_path: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        运行批量回测
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            strategies: 策略配置列表
            output_path: 可选的输出文件路径
        
        Returns:
            List[Dict[str, Any]]: 回测结果列表
        """
        results = []
        for strategy in strategies:
            result = self.single_runner.run(
                start_date=start_date,
                end_date=end_date,
                strategy=strategy
            )
            results.append(result)
        
        if output_path:
            self._save_results(results, output_path)
        
        return results
    
    def _save_results(self, results: List[Dict[str, Any]], output_path: str):
        """保存回测结果"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        results_df = pd.DataFrame([
            {
                **r['strategy'],
                **{f"metric_{k}": v for k, v in r['metrics'].items()}
            }
            for r in results
        ])
        
        results_df.to_excel(output_path, index=False)
        logger.info(f"回测结果已保存到: {output_path}") 