import uuid
import requests
import pandas as pd
import pymysql
from datetime import datetime, timedelta
import hashlib
import logging
import numpy as np
import schedule
import time


# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 配置类
class Config:
    API_NAME = "api/vlist/ExecuteQuery"
    QUERY_ID = "38c53a54-813f-a0e0-0000-06f40ebdeca5"
    PAGE_INDEX = 1
    PAGE_SIZE = 5000
    IS_USER_QUERY = True
    IS_PREVIEW = False
    PAGING = True
    CONDITIONS = '[{"name":"new_signedon","val":"not-null","op":"not-null"},{"name":"createdon","val":"before-today","op":"before-today"},{"name":"createdon","val":"60","op":"last-x-days"}]'
    DB_CONFIG = {
        'host': '172.16.101.2',
        'user': 'LJH',
        'password': 'ljhyds666',
        'database': 'demo',
        'port': 3306
    }
    TABLE_NAME = "maintenance_detail_ruiyun"

# Function to generate the API URL
def generate_sign(conditions, pageindex, pagesize, paging, reqid, timestamp, isPreview, isUserQuery, queryid, key):
    sign_str = f"AS_department{conditions}{pageindex}{pagesize}{paging}{reqid}laifen{timestamp}{isPreview}{isUserQuery}{queryid}{key}"
    return hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()

def get_url(api_name, queryid, pageindex, pagesize, isUserQuery, isPreview, paging, conditions):
    extendConditions = requests.utils.quote(conditions, safe='')
    reqid = str(uuid.uuid4())
    timestamp = str(int(datetime.now().timestamp() * 1000))
    key = "u7BDpKHA6VSqTScpEqZ4cPKmYVbQTAxgTBL2Gtit"
    sign = generate_sign(conditions, pageindex, pagesize, paging, reqid, timestamp, isPreview, isUserQuery, queryid, key)

    url = (f"https://ap6-openapi.fscloud.com.cn/t/laifen/open/{api_name}?"
           f"$tenant=laifen&$timestamp={timestamp}&$reqid={reqid}&$appid=AS_department&queryid={queryid}"
           f"&isUserQuery={isUserQuery}&isPreview={isPreview}&$pageindex={pageindex}&$pagesize={pagesize}"
           f"&$paging={paging}&$extendConditions={extendConditions}&$sign={sign}")
    return url

# Function to get data from API URL
def get_data(url):
    logging.info(f"正在请求API: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        # 检查返回数据是否包含 'Data' 字段
        if 'Data' not in data or 'Entities' not in data['Data']:
            logging.error(f"返回数据格式异常: {data}")
            return []

        logging.info(f"请求成功，返回数据：{len(data['Data']['Entities'])}条")
        return data['Data']['Entities']
    except requests.exceptions.RequestException as e:
        logging.error(f"请求失败: {e}")
        return []
    except Exception as e:
        logging.error(f"未知错误: {e}")
        return []

# Function to get a list of data
def get_list():
    logging.info("开始获取数据...")
    total_count = 0
    pages = 0
    all_data = []

    # 第一次请求，获取总数据条数和分页数
    url = get_url(Config.API_NAME, Config.QUERY_ID, Config.PAGE_INDEX, Config.PAGE_SIZE, Config.IS_USER_QUERY, Config.IS_PREVIEW, Config.PAGING, Config.CONDITIONS)
    response = requests.get(url)
    data = response.json()

    # 检查是否请求成功
    if 'Data' not in data:
        logging.error(f"请求失败，返回数据格式异常: {data}")
        return pd.DataFrame()

    total_count = data['Data']['TotalRecordCount']
    pages = (total_count + Config.PAGE_SIZE - 1) // Config.PAGE_SIZE

    logging.info(f"总数据条数: {total_count}, 分页数: {pages}")

    # 分页请求数据
    for i in range(1, pages + 1):
        logging.info(f"正在请求第{i}页数据...")
        url = get_url(Config.API_NAME, Config.QUERY_ID, i, Config.PAGE_SIZE, Config.IS_USER_QUERY, Config.IS_PREVIEW, Config.PAGING, Config.CONDITIONS)
        page_data = get_data(url)
        all_data.extend(page_data)


    df = pd.DataFrame(all_data)

    logging.info(f"获取数据完成，共计{len(df)}条数据")
    return df

# Function to process and clean the data
def process_data(a):

    logging.info("开始数据处理...")
    a_1 = a.assign(
        productmodel_name=a['new_productmodel_id'].apply(lambda x: x.get('name') if isinstance(x, dict) else None),
        product_name=a['new_product_id'].apply(lambda x: x.get('name') if isinstance(x, dict) else None),
        applytype=a['FormattedValues'].apply(lambda x: x.get('new_srv_rma_0.new_applytype')),
        new_status=a['new_srv_rma_0.new_status'],
        per_name_fenjian=a['laifen_systemuser2_id'].apply(lambda x: x.get('name') if isinstance(x, dict) else None),
        per_name_yijian=a['laifen_systemuser_id'].apply(lambda x: x.get('name') if isinstance(x, dict) else None),
        per_name_weixiu=a['new_srv_workorder_1.new_srv_worker_id'].apply(lambda x: x.get('name') if isinstance(x, dict) else None),
        new_rma_id=a['new_rma_id'].apply(lambda x: x.get('name') if isinstance(x, dict) else None),

        createdon=a['FormattedValues'].apply(lambda x: x.get('createdon')),
        new_userprofilesn=a['new_userprofilesn'],
        laifen_jstsalesorderid = a['new_srv_rma_0.laifen_jstsalesorderid'],
        new_errorclassifly_name = a['new_errorclassifly_id'].apply(lambda x: x.get('name') if pd.notnull(x) else None),
        new_error_name = a['new_error_id'].apply(lambda x: x.get('name') if pd.notnull(x) else None),
        new_fromsource = a['FormattedValues'].apply(lambda x: x.get('new_srv_rma_0.new_fromsource') if pd.notnull(x) else None),
        order_id = a['new_srv_rma_0.laifen_xdorderid'],
        new_workorder_id=a['new_workorder_id'].apply(lambda x: x.get('name') if pd.notnull(x) else None)

    )

    # Select and transform columns
    a_1 = a_1[
        ['new_rma_id', 'productmodel_name', 'product_name', 'laifen_productnumber', 'new_returnstatus', 'new_status',
         'applytype', 'per_name_fenjian', 'per_name_yijian', 'per_name_weixiu','createdon', 'new_signedon', 'new_checkon',
         'laifen_servicecompletetime', 'laifen_qualityrecordtime', 'new_deliveriedon','new_userprofilesn','laifen_jstsalesorderid',
         'new_errorclassifly_name','new_error_name','new_fromsource','order_id','new_workorder_id']]

    # Replace return status and new status using map
    returnstatus_mapping = {
        10: '待取件', 30: '已签收', 60: '已维修', 50: '维修中', 70: '已质检', 40: '已检测',
        20: '已取件', 80: '已一检', 90: '异常', 100: '一检异常', 110: '地址异常'
    }
    a_1['new_returnstatus'] = a_1['new_returnstatus'].map(returnstatus_mapping)

    status_mapping = {
        "10": "待处理", "50": "已评价", "30": "已完成", "40": "已取消", "20": "处理中",
        "60": "已检测", "80": "异常", "70": "已一检", "90": "重复待确认"
    }
    a_1['new_status'] = a_1['new_status'].map(status_mapping)

    # Convert datetime columns
    datetime_columns = ['new_signedon', 'new_checkon', 'laifen_servicecompletetime', 'laifen_qualityrecordtime', 'new_deliveriedon','createdon']
    for col in datetime_columns:
        a_1[col] = pd.to_datetime(a_1[col])

    # Replace NaN with None for MySQL compatibility
    a_1 = a_1.replace({np.nan: None})

    logging.info("数据处理完成")
    return a_1

# Function to save data to MySQL database using pymysql
def save_to_mysql(df):
    max_time = df['createdon'].max()
    min_time = df['createdon'].min()
    max_time = max_time +timedelta(days=1)

    min_time = min_time.strftime('%Y-%m-%d')
    max_time = max_time.strftime('%Y-%m-%d')
    logging.info(f"开始插入数据到数据库: {Config.TABLE_NAME}...")
    try:
        # 连接数据库
        conn = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password'],
            database=Config.DB_CONFIG['database'],
            port=Config.DB_CONFIG['port'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()

        # 清空表
        # cursor.execute(f"TRUNCATE TABLE {Config.TABLE_NAME};")
        # logging.info(f"已清空表: {Config.TABLE_NAME}")

        # 删除已经存在的即将重复的数据
        delete_sql = f"delete from maintenance_detail_ruiyun where date_format(createdon,'%Y-%m-%d %H:%i:%s') between date_format('{str(min_time)}','%Y-%m-%d') and date_format('{str(max_time)}','%Y-%m-%d');"
        logging.info(f'生成的删除语句\n{delete_sql}')
        affected_rows = cursor.execute(delete_sql)
        logging.info(f"删除了 {affected_rows} 行数据")
        # 动态生成列名和占位符
        columns = ', '.join(df.columns)  # 获取列名，并用逗号分隔
        placeholders = ', '.join(['%s'] * len(df.columns))  # 生成占位符，例如：%s, %s, %s

        # 动态生成 SQL 插入语句
        sql = f"""
            INSERT INTO {Config.TABLE_NAME} ({columns})
            VALUES ({placeholders})
        """
        logging.info(f"生成的 SQL 插入语句: {sql}")

        # 批量插入数据
        data_tuples = list(df.itertuples(index=False, name=None))
        affected_rows = cursor.executemany(sql, data_tuples)
        logging.info(f"插入了 {affected_rows} 行数据")
        conn.commit()
        logging.info(f"成功插入{len(df)}条数据")
    except pymysql.Error as e:
        logging.error(f"数据库操作失败: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Main function to execute the process
def main():
    a = get_list()
    a_1 = process_data(a)
    save_to_mysql(a_1)
    logging.info("所有任务已完成")

def job_sync_db():
    logging.info(f'任务开始运行~at{datetime.now()}')
    main()

# 程序入口
if __name__ == '__main__':
    logging.info("gogogo~")
    # job_sync_db()
    schedule.every().day.at("05:00").do(job_sync_db)
    while True:
        schedule.run_pending()
        time.sleep(1)
