#!/bin/bash

# 设置路径
APP_DIR="/www/wwwroot/convertedbondweb/monterey_backend"
VENV_DIR="$APP_DIR/venv"
REQUIREMENTS="$APP_DIR/requirements.txt"
APP_MODULE="main:app"
PORT=8001

cd "$APP_DIR"

# 如果虚拟环境不存在，则创建
if [ ! -d "$VENV_DIR" ]; then
    echo "[INFO] 创建 Python 虚拟环境..."
    python3 -m venv "$VENV_DIR"
fi

# 激活虚拟环境
source "$VENV_DIR/bin/activate"

# 安装依赖（requirements.txt 存在才装）
if [ -f "$REQUIREMENTS" ]; then
    echo "[INFO] 安装 Python 依赖..."
    pip install --upgrade pip
    pip install -r "$REQUIREMENTS"
else
    echo "[WARN] 未找到 requirements.txt，跳过依赖安装"
fi

# 启动 gunicorn + uvicorn worker
echo "[INFO] 启动后端服务..."
exec gunicorn "$APP_MODULE" \
    --workers 4 \
    --bind 0.0.0.0:$PORT \
    -k uvicorn.workers.UvicornWorker \
    --log-level=info
