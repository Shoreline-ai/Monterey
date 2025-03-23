# Convertible Bond Backtest Framework

这是一个用于可转债回测的框架。

## 安装说明

### 基础安装（仅运行功能）

```bash
pip install -e .
```

### 开发环境安装（包含所有开发工具）

```bash
pip install -r requirements-dev.txt
```

## 依赖说明

- 核心依赖（在 setup.py 中定义）：
  - pandas >= 2.2.3
  - numpy >= 2.0.2
  - TA-Lib >= 0.4.0
  - quantstats >= 0.0.62
  - openpyxl >= 3.0.10
  - pyarrow >= 8.0.0

- 开发依赖（在 requirements-dev.txt 中定义）：
  - Jupyter 环境支持
  - 开发工具（debugpy, black, flake8 等）
  - 测试工具（pytest）
  - 文档工具（Sphinx）

## 注意事项

1. 确保您的 Python 版本 >= 3.8
2. 如果您只需要使用框架的核心功能，使用基础安装即可
3. 如果您需要进行开发或贡献代码，请使用开发环境安装
