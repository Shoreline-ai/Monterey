# Convertible Bond Backtest Framework
# 可转债回测框架

[English](#english) | [中文](#chinese)

---

<a name="english"></a>
## English Version

This is a framework for backtesting convertible bonds.

### Installation Guide

#### Prerequisites

1. Install Docker
   - Download and install Docker from [Docker's official website](https://www.docker.com/products/docker-desktop)
   - Verify installation with `docker --version`

2. Set up MongoDB
   ```bash
   # Create and run a MongoDB container
   docker run --name some-mongo -d -p 27017:27017 mongo:latest
   ```

3. Install Python Dependencies
   ```bash
   # Install Flask and MongoDB dependencies
   pip install flask flask-cors pymongo python-dotenv
   ```

#### Basic Installation (Runtime Only)

```bash
pip install -e .
```

#### Development Environment Installation (Includes All Dev Tools)

```bash
pip install -r requirements-dev.txt
```

### Dependencies

- Core Dependencies (defined in setup.py):
  - pandas >= 2.2.3
  - numpy >= 2.0.2
  - TA-Lib >= 0.4.0
  - quantstats >= 0.0.62
  - openpyxl >= 3.0.10
  - pyarrow >= 8.0.0
  - flask
  - flask-cors
  - pymongo
  - python-dotenv

- Development Dependencies (defined in requirements-dev.txt):
  - Jupyter environment support
  - Development tools (debugpy, black, flake8, etc.)
  - Testing tools (pytest)
  - Documentation tools (Sphinx)

### Important Notes

1. Ensure your Python version is >= 3.8
2. If you only need the core functionality of the framework, use the basic installation
3. If you need to develop or contribute code, please use the development environment installation
4. Make sure MongoDB is running before starting the application

---

<a name="chinese"></a>
## 中文版本

这是一个用于可转债回测的框架。

### 安装说明

#### 前置要求

1. 安装 Docker
   - 从 [Docker 官网](https://www.docker.com/products/docker-desktop) 下载并安装 Docker
   - 使用 `docker --version` 验证安装

2. 设置 MongoDB
   ```bash
   # 创建并运行 MongoDB 容器
   docker run --name some-mongo -d -p 27017:27017 mongo:latest
   ```

3. 安装 Python 依赖
   ```bash
   # 安装 Flask 和 MongoDB 依赖
   pip install flask flask-cors pymongo python-dotenv
   ```

#### 基础安装（仅运行功能）

```bash
pip install -e .
```

#### 开发环境安装（包含所有开发工具）

```bash
pip install -r requirements-dev.txt
```

### 依赖说明

- 核心依赖（在 setup.py 中定义）：
  - pandas >= 2.2.3
  - numpy >= 2.0.2
  - TA-Lib >= 0.4.0
  - quantstats >= 0.0.62
  - openpyxl >= 3.0.10
  - pyarrow >= 8.0.0
  - flask
  - flask-cors
  - pymongo
  - python-dotenv

- 开发依赖（在 requirements-dev.txt 中定义）：
  - Jupyter 环境支持
  - 开发工具（debugpy, black, flake8 等）
  - 测试工具（pytest）
  - 文档工具（Sphinx）

### 注意事项

1. 确保您的 Python 版本 >= 3.8
2. 如果您只需要使用框架的核心功能，使用基础安装即可
3. 如果您需要进行开发或贡献代码，请使用开发环境安装
4. 在启动应用程序之前，请确保 MongoDB 正在运行
