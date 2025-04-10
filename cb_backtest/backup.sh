#!/bin/bash

# 备份配置
BACKUP_DIR="/www/backup/cb_backtest"
KEEP_DAYS=7
DATE=$(date +%Y%m%d)
PROJECT_DIR="/www/wwwroot/cb_backtest"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份代码
echo "开始备份代码..."
cd /www/wwwroot
tar -czf $BACKUP_DIR/cb_backtest_code_$DATE.tar.gz cb_backtest/
echo "代码备份完成"

# 备份数据（根据实际数据目录修改）
echo "开始备份数据..."
if [ -d "/path/to/your/data" ]; then
    cd /path/to/your/data
    tar -czf $BACKUP_DIR/cb_backtest_data_$DATE.tar.gz ./*
    echo "数据备份完成"
else
    echo "数据目录不存在，跳过数据备份"
fi

# 删除旧备份
echo "清理旧备份..."
find $BACKUP_DIR -mtime +$KEEP_DAYS -name "*.tar.gz" -exec rm {} \;
echo "旧备份清理完成"

# 列出当前备份文件
echo "当前备份文件列表："
ls -lh $BACKUP_DIR

# 检查备份文件大小
echo "备份文件大小统计："
du -sh $BACKUP_DIR/*

echo "备份完成" 