import argparse
import sys
from pathlib import Path
import json
import logging
from typing import Optional

# 添加父目录到系统路径以导入核心模块
sys.path.append(str(Path(__file__).parent.parent))
from core import BatchRunner

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def run_from_config(config_path: str):
    """从配置文件运行回测"""
    runner = BatchRunner(
        cb_data_path=config['data']['cb_data_path'],
        index_data_path=config['data']['index_data_path']
    )
    return runner.run_from_config(config_path)

def run_single_strategy(
    cb_data_path: str,
    index_data_path: str,
    start_date: str,
    end_date: str,
    strategy_path: Optional[str] = None,
    strategy_json: Optional[str] = None
):
    """运行单个策略"""
    if strategy_path:
        with open(strategy_path, 'r') as f:
            strategy = json.load(f)
    elif strategy_json:
        strategy = json.loads(strategy_json)
    else:
        raise ValueError("必须提供strategy_path或strategy_json其中之一")

    runner = BatchRunner(cb_data_path=cb_data_path, index_data_path=index_data_path)
    result = runner.run_single(
        start_date=start_date,
        end_date=end_date,
        strategy=strategy
    )
    return result

def main():
    parser = argparse.ArgumentParser(description='可转债回测脚本')
    subparsers = parser.add_subparsers(dest='command', help='运行模式')

    # 配置文件模式
    config_parser = subparsers.add_parser('config', help='使用配置文件运行')
    config_parser.add_argument('config_path', help='配置文件路径')

    # 单策略模式
    single_parser = subparsers.add_parser('single', help='运行单个策略')
    single_parser.add_argument('--cb_data_path', required=True, help='可转债数据路径')
    single_parser.add_argument('--index_data_path', required=True, help='指数数据路径')
    single_parser.add_argument('--start_date', required=True, help='开始日期')
    single_parser.add_argument('--end_date', required=True, help='结束日期')
    single_parser.add_argument('--strategy_path', help='策略配置文件路径')
    single_parser.add_argument('--strategy_json', help='策略配置JSON字符串')

    args = parser.parse_args()

    try:
        if args.command == 'config':
            results = run_from_config(args.config_path)
            logger.info("批量回测完成")
            
        elif args.command == 'single':
            result = run_single_strategy(
                cb_data_path=args.cb_data_path,
                index_data_path=args.index_data_path,
                start_date=args.start_date,
                end_date=args.end_date,
                strategy_path=args.strategy_path,
                strategy_json=args.strategy_json
            )
            logger.info(f"单策略回测完成，结果：{json.dumps(result, indent=2)}")
            
        else:
            parser.print_help()
            
    except Exception as e:
        logger.error(f"运行出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 