# 宝塔面板部署指南

## 一、环境准备

### 1. 宝塔面板安装
1. 安装 Python 项目管理器
2. 安装 Python 3.8 或更高版本
3. 安装 Nginx
4. 安装 Redis（如果需要）

### 2. 安装路径说明
- 项目路径：`/www/wwwroot/cb_backtest`
- Python 虚拟环境：`/www/wwwroot/cb_backtest/venv`
- 日志路径：`/www/wwwroot/cb_backtest/logs`
  - access.log：访问日志
  - error.log：错误日志
  - gunicorn.pid：进程 ID 文件
  - backtest.log：回测日志
- Nginx 日志：`/www/wwwlogs/cb_backtest.log`

## 二、部署步骤

### 1. 创建网站
1. 在宝塔面板中选择"网站"
2. 点击"添加站点"
3. 填写域名信息
4. 选择 PHP 版本为"纯静态"
5. 创建完成后会自动生成网站目录

### 2. 上传代码
1. 使用 SFTP 或 Git 将代码上传到 `/www/wwwroot/cb_backtest/`
2. 确保包含以下文件：
   - requirements.txt
   - gunicorn_config.py
   - start.sh
   - bt_config.json
   - nginx.conf（参考配置）

### 3. 配置 Python 环境
```bash
# 进入项目目录
cd /www/wwwroot/cb_backtest

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 设置权限
chown -R www:www /www/wwwroot/cb_backtest
chmod +x start.sh

# 创建日志目录
mkdir -p logs
chown -R www:www logs
```

### 4. 配置 Python 项目
1. 在宝塔面板中选择"Python项目"
2. 点击"添加项目"
3. 填写配置信息：
   - 项目名称：cb_backtest
   - 项目路径：/www/wwwroot/cb_backtest
   - Python 版本：3.8
   - 启动方式：gunicorn
   - 启动文件：start.sh
   - 是否守护进程：是
   - 开机启动：是

### 5. 配置 Nginx
1. 在宝塔面板中选择"网站"
2. 找到您的站点，点击"设置"
3. 选择"配置文件"
4. 将 nginx.conf 中的配置复制进去，注意修改：
   - server_name：改为您的实际域名
   - 如果需要 SSL，添加相应配置

### 6. 启动服务
1. 在 Python 项目管理器中启动项目
2. 检查日志文件：
   ```bash
   tail -f /www/wwwroot/cb_backtest/logs/access.log
   tail -f /www/wwwroot/cb_backtest/logs/error.log
   ```

## 三、数据配置

### 1. 数据文件路径
确保数据文件位于正确的位置，并且具有正确的权限：
```bash
# 设置数据目录权限
chown -R www:www /path/to/your/data
chmod 755 /path/to/your/data
```

### 2. 配置文件检查
确保以下配置文件中的路径正确：
- gunicorn_config.py
- bt_config.json
- nginx.conf

## 四、维护指南

### 1. 服务管理
```bash
# 启动服务
cd /www/wwwroot/cb_backtest
./start.sh

# 停止服务
kill -9 $(cat logs/gunicorn.pid)

# 重启服务
kill -HUP $(cat logs/gunicorn.pid)
```

### 2. 日志管理
```bash
# 查看访问日志
tail -f /www/wwwroot/cb_backtest/logs/access.log

# 查看错误日志
tail -f /www/wwwroot/cb_backtest/logs/error.log

# 查看回测日志
tail -f /www/wwwroot/cb_backtest/logs/backtest.log

# 查看 Nginx 日志
tail -f /www/wwwlogs/cb_backtest.log
tail -f /www/wwwlogs/cb_backtest.error.log
```

### 3. 备份策略
建议设置定时任务进行数据备份：
1. 在宝塔面板中选择"计划任务"
2. 添加定时备份任务
3. 示例备份脚本：
```bash
#!/bin/bash
backup_dir="/www/backup/cb_backtest"
date_str=$(date +%Y%m%d)
mkdir -p $backup_dir
cd /www/wwwroot/cb_backtest
tar -czf $backup_dir/cb_backtest_$date_str.tar.gz ./*
find $backup_dir -mtime +7 -name "*.tar.gz" -exec rm {} \;
```

## 五、故障排查

### 1. 常见问题
1. 服务无法启动
   - 检查端口是否被占用
   - 检查日志文件
   - 检查权限设置

2. 502 错误
   - 检查 gunicorn 是否正常运行
   - 检查 socket 文件权限
   - 检查 Nginx 配置

3. 数据访问错误
   - 检查数据文件权限
   - 检查数据文件路径配置

### 2. 日志位置
- Gunicorn 日志：/www/wwwroot/cb_backtest/logs/
- Nginx 日志：/www/wwwlogs/
- Python 错误日志：/www/wwwroot/cb_backtest/logs/error.log

### 3. 性能优化
1. 调整 gunicorn 工作进程数
2. 优化 Nginx 配置
3. 监控内存使用情况

## 六、安全建议

1. 设置防火墙规则
2. 配置 SSL 证书
3. 定期更新系统和依赖包
4. 设置访问控制
5. 配置数据备份

## 七、更新维护

### 1. 代码更新流程
```bash
# 1. 备份当前版本
cd /www/wwwroot
tar -czf cb_backtest_backup_$(date +%Y%m%d).tar.gz cb_backtest/

# 2. 更新代码
cd /www/wwwroot/cb_backtest
git pull  # 如果使用 git

# 3. 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 4. 重启服务
kill -HUP $(cat logs/gunicorn.pid)
```

### 2. 版本回滚
```bash
# 如果需要回滚
cd /www/wwwroot
rm -rf cb_backtest
tar -xzf cb_backtest_backup_20240330.tar.gz
cd cb_backtest
./start.sh
``` 