"""文件操作模块

提供文件和目录操作相关的工具函数。
"""

import os
import shutil
from pathlib import Path
from typing import Union, List
from .logger import logger

def ensure_directory(path: Union[str, Path]) -> Path:
    """确保目录存在，如果不存在则创建
    
    Args:
        path: 目录路径
        
    Returns:
        Path对象
        
    Raises:
        OSError: 创建目录失败时抛出
    """
    try:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        return path
    except Exception as e:
        logger.error(f"创建目录失败: {path}")
        raise OSError(f"无法创建目录 {path}: {str(e)}") from e

def safe_remove(path: Union[str, Path]) -> bool:
    """安全删除文件或目录
    
    Args:
        path: 文件或目录路径
        
    Returns:
        是否成功删除
    """
    try:
        path = Path(path)
        if not path.exists():
            return False
        
        if path.is_file():
            path.unlink()
        else:
            shutil.rmtree(path)
        return True
    except Exception as e:
        logger.error(f"删除失败: {path}")
        return False

def list_files(
    directory: Union[str, Path], 
    pattern: str = "*",
    recursive: bool = False
) -> List[Path]:
    """列出目录中的文件
    
    Args:
        directory: 目录路径
        pattern: 文件匹配模式
        recursive: 是否递归搜索子目录
        
    Returns:
        文件路径列表
    """
    directory = Path(directory)
    if recursive:
        return list(directory.rglob(pattern))
    return list(directory.glob(pattern)) 