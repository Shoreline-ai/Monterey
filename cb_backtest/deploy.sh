#!/bin/bash

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 root 权限运行此脚本"
    exit 1
fi

# 设置工作目录
cd /www/wwwroot/cb_backtest

# 创建必要的目录
mkdir -p data logs

# 设置项目目录权限
chown -R www:www /www/wwwroot/cb_backtest

# 设置启动脚本执行权限
chmod +x start.sh

# 设置日志目录权限
chmod 755 logs
chown -R www:www logs

# 设置数据目录权限
chmod 755 data
chown -R www:www data

echo "权限设置完成！"
echo "请确保："
echo "1. 数据文件已上传到 data 目录"
echo "2. 配置文件已正确设置"
echo "3. 宝塔面板中的项目配置已完成" 