#!/bin/bash

# 项目信息
PROJECT_NAME="cb_backtest"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

echo "🧠 启动项目: $PROJECT_NAME"
echo "📂 项目路径: $PROJECT_ROOT"

cd "$PROJECT_ROOT" || {
    echo "❌ 无法进入项目目录: $PROJECT_ROOT"
    exit 1
}

# 创建目录
mkdir -p logs data

# 设置权限（仅在 Linux 且为 root 用户）
if [[ "$OSTYPE" == "linux-gnu"* ]] && [ "$EUID" -eq 0 ]; then
    echo "🔧 设置目录权限..."
    chown -R www:www "$PROJECT_ROOT"
    chmod 755 logs data
    chown -R www:www logs data
fi

# 自动识别虚拟环境路径
if [ -f "${PROJECT_ROOT}/.venv/bin/activate" ]; then
    VENV_PATH="${PROJECT_ROOT}/.venv"
    echo "🧪 使用本地虚拟环境: .venv"
elif [ -f "/www/server/py-project-env/${PROJECT_NAME}/bin/activate" ]; then
    VENV_PATH="/www/server/py-project-env/${PROJECT_NAME}"
    echo "🧪 使用宝塔默认虚拟环境"
else
    echo "❌ 未找到虚拟环境，请手动创建 .venv"
    exit 1
fi

# 激活虚拟环境
source "${VENV_PATH}/bin/activate"

# 设置 PYTHONPATH
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
echo "🐍 PYTHONPATH: $PYTHONPATH"

# 使用 aliyun pip 镜像（可选）
PIP_CONF_DIR="$HOME/.config/pip"
mkdir -p "$PIP_CONF_DIR"
cat > "$PIP_CONF_DIR/pip.conf" <<EOF
[global]
index-url = https://mirrors.aliyun.com/pypi/simple
timeout = 180
EOF

echo "📦 pip 镜像: aliyun | 超时: 180s"

# 安装依赖（带重试）
MAX_RETRIES=3
for ((i=1; i<=MAX_RETRIES; i++)); do
    if pip install -r requirements.txt; then
        echo "✅ 依赖安装成功"
        break
    else
        echo "⚠️ 第 $i 次依赖安装失败，重试中..."
        sleep 5
    fi
done

# 启动 Gunicorn + UvicornWorker
echo "🚀 启动 gunicorn 服务..."
WORKER_CLASS="uvicorn.workers.UvicornWorker"

exec gunicorn cb_backtest.api.app:app \
    --chdir "$PROJECT_ROOT" \
    --worker-class "$WORKER_CLASS" \
    --bind 127.0.0.1:8000 \
    --reload \
    --log-level debug \
    --access-logfile - \
    --error-logfile -