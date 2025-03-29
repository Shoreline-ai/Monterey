"""工具函数包

此包包含了回测系统所需的各种工具函数，按功能分类：
- logger: 日志配置和管理
- date: 日期解析和处理
- data: 数据处理和计算
- file: 文件和目录操作
- validation: 数据验证
- metrics: 性能指标计算
"""

from .logger import setup_logger, logger
from .date import parse_date, date_range
from .data import safe_divide, round_dict
from .file import ensure_directory
from .validation import validate_weights, validate_date_order
from .metrics import calculate_drawdown, calculate_sharpe_ratio

__all__ = [
    'setup_logger',
    'logger',
    'parse_date',
    'date_range',
    'safe_divide',
    'round_dict',
    'ensure_directory',
    'validate_weights',
    'validate_date_order',
    'calculate_drawdown',
    'calculate_sharpe_ratio',
] 