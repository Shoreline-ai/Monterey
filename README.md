# Convertible Bond Backtest Framework
# 可转债回测框架

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English Version

A high-performance framework for backtesting convertible bond trading strategies, featuring:
- Factor-based strategy development
- Single and batch backtesting
- Performance evaluation
- RESTful API service

### Installation Guide

#### Prerequisites

1. Python Environment
   - Ensure Python >= 3.8 is installed
   - Create and activate a virtual environment (recommended):
     ```bash
     python -m venv .venv
     source .venv/bin/activate  # On Windows: .venv\Scripts\activate
     ```

2. Installation Options

   a. For Users (Install Dependencies Only)
   ```bash
   cd cb_backtest
   pip install -r requirements.txt
   ```
   This will install all required third-party packages for running the service.

   b. For Developers (Install with Development Tools)
   ```bash
   cd cb_backtest
   pip install -r requirements-dev.txt
   ```
   This will:
   - Install the project in editable mode
   - Install all development tools (Jupyter, testing, formatting)
   - Enable instant code changes without reinstallation

### Dependency Management

The project uses a three-tier dependency management system:

1. `pyproject.toml`:
   - Defines project metadata and dependencies
   - Uses `>=` for core dependencies (minimum version requirements)
   - Uses `==` for API and development tools (fixed versions)
   - Supports optional dependency groups (dev/test/docs)

2. `requirements.txt`:
   - Lists all runtime dependencies with fixed versions
   - Ensures production environment consistency
   - Used for deployment and production

3. `requirements-dev.txt`:
   - Includes all development tools
   - References the project itself in editable mode
   - Used for development environment setup

### Running the Service

1. Start the FastAPI Service
   ```bash
   python -m uvicorn cb_backtest.api.app:app --host 127.0.0.1 --port 8000
   ```

2. Access the API Documentation
   - Open http://127.0.0.1:8000/docs in your browser
   - You can test the API directly through the Swagger UI

### API Usage Example

```python
import requests
import json

url = "http://127.0.0.1:8000/backtest/run"
data = {
    "data": {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    },
    "strategy": {
        "exclude_conditions": ["低于面值", "已到期"],
        "score_factors": ["到期收益率", "剩余期限"],
        "weights": [0.7, 0.3],
        "hold_num": 20,
        "stop_profit": 0.2,
        "fee_rate": 0.003
    }
}

response = requests.post(url, json=data)
results = response.json()
```

### Project Structure

```
cb_backtest/
├── api/                # FastAPI service
│   ├── app.py         # API endpoints
│   ├── models.py      # Request/Response models
│   └── config.yaml    # Service configuration
├── core/              # Core backtest logic
│   ├── backtester.py  # Main backtester implementation
│   ├── engine.py      # Factor engine
│   ├── eval.py        # Performance evaluation
│   ├── single_runner.py # Single backtest runner
│   └── batch_runner.py # Batch backtest runner
└── utils/             # Utility functions
```

### Development Tools

The project includes several development tools:

1. Code Quality:
   - `black`: Code formatting
   - `flake8`: Style guide enforcement
   - `isort`: Import sorting

2. Testing:
   - `pytest`: Unit testing

3. Documentation:
   - `Sphinx`: Documentation generation
   - `sphinx-rtd-theme`: ReadTheDocs theme

4. Jupyter Support:
   - Full Jupyter notebook support for strategy development
   - Interactive debugging capabilities

---

<a name="chinese"></a>
## 中文版本

这是一个高性能的可转债回测框架，特点包括：
- 因子策略开发
- 单次和批量回测
- 性能评估
- RESTful API 服务

### 安装说明

#### 前置要求

1. Python 环境
   - 确保安装了 Python >= 3.8
   - 创建并激活虚拟环境（推荐）：
     ```bash
     python -m venv .venv
     source .venv/bin/activate  # Windows 系统：.venv\Scripts\activate
     ```

2. 安装选项

   a. 普通用户（仅安装运行依赖）
   ```bash
   cd cb_backtest
   pip install -r requirements.txt
   ```
   这将安装运行服务所需的所有第三方包。

   b. 开发者（安装开发工具）
   ```bash
   cd cb_backtest
   pip install -r requirements-dev.txt
   ```
   这将：
   - 以可编辑模式安装项目
   - 安装所有开发工具（Jupyter、测试、代码格式化）
   - 支持即时代码修改，无需重新安装

### 依赖管理

项目使用三层依赖管理系统：

1. `pyproject.toml`：
   - 定义项目元数据和依赖
   - 核心依赖使用 `>=` 指定最低版本要求
   - API 和开发工具使用 `==` 固定版本
   - 支持可选依赖分组（dev/test/docs）

2. `requirements.txt`：
   - 列出所有运行时依赖的固定版本
   - 确保生产环境的一致性
   - 用于部署和生产环境

3. `requirements-dev.txt`：
   - 包含所有开发工具
   - 以可编辑模式引用项目本身
   - 用于开发环境搭建

### 运行服务

1. 启动 FastAPI 服务
   ```bash
   python -m uvicorn cb_backtest.api.app:app --host 127.0.0.1 --port 8000
   ```

2. 访问 API 文档
   - 在浏览器中打开 http://127.0.0.1:8000/docs
   - 可以直接通过 Swagger UI 测试 API

### API 使用示例

```python
import requests
import json

url = "http://127.0.0.1:8000/backtest/run"
data = {
    "data": {
        "start_date": "2023-01-01",
        "end_date": "2023-12-31"
    },
    "strategy": {
        "exclude_conditions": ["低于面值", "已到期"],
        "score_factors": ["到期收益率", "剩余期限"],
        "weights": [0.7, 0.3],
        "hold_num": 20,
        "stop_profit": 0.2,
        "fee_rate": 0.003
    }
}

response = requests.post(url, json=data)
results = response.json()
```

### 项目结构

```
cb_backtest/
├── api/                # FastAPI 服务
│   ├── app.py         # API 端点
│   ├── models.py      # 请求/响应模型
│   └── config.yaml    # 服务配置
├── core/              # 核心回测逻辑
│   ├── backtester.py  # 主要回测器实现
│   ├── engine.py      # 因子引擎
│   ├── eval.py        # 性能评估
│   ├── single_runner.py # 单次回测运行器
│   └── batch_runner.py # 批量回测运行器
└── utils/             # 工具函数
```

### 开发工具

项目包含多个开发工具：

1. 代码质量：
   - `black`：代码格式化
   - `flake8`：代码风格检查
   - `isort`：导入语句排序

2. 测试：
   - `pytest`：单元测试

3. 文档：
   - `Sphinx`：文档生成
   - `sphinx-rtd-theme`：ReadTheDocs 主题

4. Jupyter 支持：
   - 完整的 Jupyter notebook 支持，用于策略开发
   - 交互式调试功能
