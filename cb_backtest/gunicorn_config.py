import multiprocessing
import os

# 获取项目根目录
project_dir = os.path.dirname(os.path.abspath(__file__))

# 创建日志目录
log_dir = os.path.join(project_dir, "logs")
os.makedirs(log_dir, exist_ok=True)

# 工作进程数 (建议值: CPU核心数 * 2 + 1)
workers = multiprocessing.cpu_count() * 2 + 1

# 每个工作进程的线程数
threads = 4

# 工作模式 - 使用 uvicorn 的 worker
worker_class = 'uvicorn.workers.UvicornWorker'

# 绑定地址 - 开发模式使用本地端口，生产模式使用 Unix Socket
bind = '127.0.0.1:8000' if os.getenv('GUNICORN_MODE') == 'dev' else 'unix:/tmp/cb_backtest.sock'

# 超时设置
timeout = 120
keepalive = 5
graceful_timeout = 120

# 连接相关
backlog = 2048
max_requests = 4000
max_requests_jitter = 500
worker_connections = 1000

# 安全设置
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# 日志配置
accesslog = os.path.join(log_dir, "access.log") if os.getenv('GUNICORN_MODE') != 'dev' else '-'
errorlog = os.path.join(log_dir, "error.log") if os.getenv('GUNICORN_MODE') != 'dev' else '-'
loglevel = 'debug' if os.getenv('GUNICORN_MODE') == 'dev' else 'info'
access_log_format = '%({x-real-ip}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# 进程名称
proc_name = 'cb_backtest'

# 进程相关
daemon = False if os.getenv('GUNICORN_MODE') == 'dev' else True
pidfile = os.path.join(log_dir, "gunicorn.pid")
umask = 0o022
preload_app = True

# 用户和组设置（生产环境）
user = "www"
group = "www"

# 启动前和启动后的钩子
def on_starting(server):
    """服务启动前执行"""
    pass

def on_reload(server):
    """重新加载时执行"""
    pass

def post_fork(server, worker):
    """Fork 工作进程后执行"""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    """Fork 工作进程前执行"""
    pass

def pre_exec(server):
    """执行新的可执行文件前执行"""
    server.log.info("Forked child, re-executing.") 