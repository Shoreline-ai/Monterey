# 可转债回测系统

## 项目说明
本系统提供可转债回测服务，支持自定义策略的回测分析。系统采用 FastAPI + Gunicorn 构建，提供高性能的回测 API 服务。

## 开发环境 vs 生产环境
### 开发环境
使用开发模式运行：
```bash
# 1. 进入项目目录
cd cb_backtest

# 2. 设置执行权限（首次运行时）
chmod +x start.sh

# 3. 启动开发服务
GUNICORN_MODE=dev ./start.sh
```
特点：
- 自动检测并使用本地虚拟环境（.venv）
- 绑定到 127.0.0.1:8001
- 支持代码热重载
- 日志直接输出到控制台
- 适合本地开发和测试

> 注意：确保您在正确的目录下运行脚本。如果在其他目录，请使用完整路径：
> ```bash
> # 使用完整路径运行
> cd /path/to/your/cb_backtest  # 替换为您的实际项目路径
> GUNICORN_MODE=dev ./start.sh
> ```

### 生产环境
使用生产模式运行：
```bash
# 生产环境使用
./start.sh
```
特点：
- 自动使用宝塔面板虚拟环境
- 使用 gunicorn_config.py 中的配置
- 通过 Unix Socket 与 Nginx 整合
- 多进程管理和自动重启
- 日志写入文件系统

## 系统要求
- Python 3.9+
- Nginx
- 宝塔面板（推荐）

## 目录结构
```
/www/wwwroot/cb_backtest/
├── api/                  # API 相关代码
│   ├── app.py           # FastAPI 应用
│   ├── models.py        # 数据模型
│   └── config.yaml      # API 配置
├── core/                 # 核心回测逻辑
├── utils/               # 工具函数
├── data/                # 数据文件目录
│   ├── cb_data.pq      # 可转债数据
│   └── index.pq        # 指数数据
├── logs/                # 日志目录
│   ├── access.log      # 访问日志
│   ├── error.log       # 错误日志
│   ├── backtest.log    # 回测日志
│   └── gunicorn.pid    # 进程ID文件
├── .venv/               # Python 虚拟环境
├── start.sh            # 启动脚本
├── gunicorn_config.py  # Gunicorn 配置
├── bt_config.json      # 宝塔项目配置
└── nginx.conf          # Nginx 配置参考
```

## 部署步骤

### 1. 环境准备
```bash
# 首次部署时，使用 root 权限运行部署脚本
sudo ./deploy.sh

# 脚本会自动：
# - 创建必要的目录
# - 设置正确的权限
# - 设置启动脚本执行权限

# 创建虚拟环境
python3.9 -m venv .venv

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据准备
```bash
# 创建数据目录
mkdir -p data

# 上传数据文件
# - data/cb_data.pq
# - data/index.pq

# 设置权限
chown -R www:www data
```

### 3. 配置文件
1. 修改 `api/config.yaml` 中的数据文件路径
2. 确认 `gunicorn_config.py` 中的进程配置
3. 配置 `nginx.conf` 中的域名

### 4. 宝塔面板配置
1. 进入宝塔面板 Python 项目管理
2. 点击"添加项目"
3. 基本信息填写：
   - 项目名称：cb_backtest
   - 项目路径：/www/wwwroot/cb_backtest
   - 项目运行方式：**选择"命令行启动"**
   - 启动命令：/www/wwwroot/cb_backtest/start.sh
   - 项目状态：启用
   - 开机启动：是
   - 备注：可转债回测系统

4. 环境变量配置（点击"环境变量"按钮）：
   ```bash
   # 添加以下环境变量
   PYTHONPATH=/www/wwwroot/cb_backtest
   PATH=/www/server/pyporject_evn/cb_backtest_venv/bin:$PATH
   ```

5. 虚拟环境说明：
   - 不需要在宝塔面板中配置虚拟环境
   - 虚拟环境的激活已经在 `start.sh` 中处理
   - 环境变量中的 PATH 设置确保使用虚拟环境中的 Python

> 注意事项：
> 1. 不要选择"Gunicorn"方式启动
> 2. 不要在宝塔面板中配置虚拟环境
> 3. 确保 start.sh 有执行权限：`chmod +x start.sh`
> 4. 确保 www 用户有权限访问虚拟环境：`chown -R www:www .venv`

### 5. 服务启动
```bash
# 启动服务
./start.sh

# 查看日志
tail -f logs/access.log
tail -f logs/error.log
tail -f logs/backtest.log
```

## API 文档
- API 文档界面：`http://your_domain/docs`
- 回测接口：`POST /backtest`
- 健康检查：`GET /health`

## 回测请求示例
```python
{
    "data": {
        "start_date": "20240101",
        "end_date": "20241231"
    },
    "strategy": {
        "exclude_conditions": [
            "close < 102",
            "close > 155"
        ],
        "score_factors": [
            "bond_prem",
            "ytm"
        ],
        "weights": [
            -10,
            10
        ],
        "hold_num": 5,
        "stop_profit": 0.03,
        "fee_rate": 0.002
    }
}
```

## 维护指南

### 日志管理
- 日志文件位于 `logs` 目录
- 日志自动轮转，保留最近 5 个备份
- 单个日志文件最大 10MB

### 服务管理
```bash
# 重启服务
kill -HUP $(cat logs/gunicorn.pid)

# 停止服务
kill -9 $(cat logs/gunicorn.pid)
```

### 性能调优
- 在 `gunicorn_config.py` 中调整工作进程数
- 默认进程数 = CPU核心数 * 2 + 1
- 每个进程默认 4 个线程

## 注意事项
1. 确保数据文件路径配置正确
2. 定期检查日志文件大小
3. 建议配置 SSL 证书
4. 定期备份数据文件

## 故障排查
1. 查看错误日志：`tail -f logs/error.log`
2. 检查进程状态：`ps aux | grep gunicorn`
3. 检查端口占用：`lsof -i :80`
4. 检查权限问题：`ls -la logs/`

## 联系方式
如有问题请联系管理员 

# 设置项目目录权限
chown -R www:www /www/wwwroot/cb_backtest

# 设置启动脚本执行权限
chmod +x /www/wwwroot/cb_backtest/start.sh 

# 按 Ctrl+C 停止服务
# 或者找到进程 ID 后 kill
pkill -f gunicorn 