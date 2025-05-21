import pandas as pd
import mysql.connector
from datetime import datetime
from tqdm import tqdm
import numpy as np

def upload_cb_data_to_db(start_date, end_date, batch_size=1000):
    """
    将 cb_data.pq 中的数据上传到数据库
    
    参数:
    start_date: str, 格式 'YYYYMMDD'
    end_date: str, 格式 'YYYYMMDD'
    batch_size: int, 每批上传的数据量
    """
    # 数据库连接配置
    db_config = {
        'user': 'root',
        'password': 'St7950819',
        'host': 'sh-cynosdbmysql-grp-ed8g46uu.sql.tencentcdb.com',
        'port': '21582',
        'database': 'cb_bond'
    }
    
    try:
        # 读取 Parquet 文件
        print("读取数据文件...")
        df = pd.read_parquet('/Users/yiwei/Desktop/git/cb_data.pq')
        
        # 确保索引被重置为列
        df = df.reset_index()
        
        # 过滤日期范围
        df['trade_date'] = pd.to_datetime(df['trade_date'])
        mask = (df['trade_date'] >= pd.to_datetime(start_date)) & (df['trade_date'] <= pd.to_datetime(end_date))
        df = df[mask]
        
        if len(df) == 0:
            print("指定日期范围内没有数据")
            return
        
        # 处理数据类型
        # 将所有浮点数转换为有限值
        float_columns = df.select_dtypes(include=['float64']).columns
        for col in float_columns:
            df[col] = df[col].replace([np.inf, -np.inf], np.nan)
        
        # 将日期列转换为正确的格式
        date_columns = ['trade_date', 'list_date', 'conv_start_date', 'conv_end_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col]).dt.strftime('%Y-%m-%d')
        
        # 准备插入语句
        columns = df.columns.tolist()
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join(columns)
        
        insert_query = f"""
        INSERT INTO cb_schema.cb_data ({columns_str})
        VALUES ({placeholders})
        ON DUPLICATE KEY UPDATE
        """
        # 添加 ON DUPLICATE KEY UPDATE 子句
        update_str = ', '.join([f"{col} = VALUES({col})" for col in columns if col not in ['id']])
        insert_query += update_str
        
        # 连接数据库
        print("连接数据库...")
        cnx = mysql.connector.connect(**db_config)
        cursor = cnx.cursor()
        
        # 分批上传数据
        total_rows = len(df)
        num_batches = (total_rows + batch_size - 1) // batch_size
        
        print(f"开始上传数据，总共 {total_rows} 行，分 {num_batches} 批处理...")
        
        for i in tqdm(range(0, total_rows, batch_size)):
            batch_df = df.iloc[i:i+batch_size]
            
            # 准备批量数据
            batch_data = [tuple(x) for x in batch_df.replace({np.nan: None}).values]
            
            try:
                cursor.executemany(insert_query, batch_data)
                cnx.commit()
            except mysql.connector.Error as err:
                print(f"批次 {i//batch_size + 1} 出错: {err}")
                cnx.rollback()
                continue
        
        print("数据上传完成！")
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        raise
    
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'cnx' in locals():
            cnx.close()
            print("数据库连接已关闭")

# 使用示例
if __name__ == "__main__":
    # 设置开始和结束日期
    start_date = '20250101'  # 示例日期
    end_date = '20250101'    # 示例日期
    
    # 上传数据
    upload_cb_data_to_db(start_date, end_date)