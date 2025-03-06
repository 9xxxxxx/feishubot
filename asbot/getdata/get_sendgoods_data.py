import requests
import time
import uuid
import hashlib
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from my_utility import logger

# 获取售后物流数据

conn = create_engine("mysql+pymysql://root:000000@localhost/demo")
p_by_r = pd.read_sql('select 地区,省份 from provinces_by_region', con=conn)


def generate_jxnrequrl(pageindex, conditions=None):
    """
    从 API 获取数据并转换为 DataFrame
    """
    # 基本参数
    tenant = "laifen"
    api_name = "api/vlist/ExecuteQuery"
    timestamp = str(int(time.time() * 1000))
    reqid = str(uuid.uuid1())
    appid = "AS_department"
    key = "u7BDpKHA6VSqTScpEqZ4cPKmYVbQTAxgTBL2Gtit"
    is_user_query = "true"
    is_preview = "false"
    paging = "true"
    queryid = "6b8b0a54-813f-a029-0000-07043254fb90"

    pagesize = "5000"

    args = [appid, pageindex, pagesize, paging, reqid, tenant, timestamp, is_preview, is_user_query, queryid, key]

    """
    生成签名
    """

    sign_str = "".join(args)
    sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()
    # 构建 URL
    url = (
        f"https://ap6-openapi.fscloud.com.cn/t/{tenant}/open/{api_name}"
        f"?$tenant={tenant}&$timestamp={timestamp}&$reqid={reqid}&$appid={appid}"
        f"&queryid={queryid}&isUserQuery={is_user_query}&isPreview={is_preview}"
        f"&$pageindex={pageindex}&$pagesize={pagesize}&$paging={paging}"
        f"&$sign={sign}"
    )

    return url


def fetch_api_data(url):
    # 发送 GET 请求
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API 请求失败，状态码: {response.status_code}")

    # 解析 JSON 数据
    data = response.json()
    entities = data["Data"]["Entities"]

    df = pd.DataFrame(entities)

    return df


def extract_need_data(df):
    df = df.assign(
        创建时间=df['FormattedValues'].apply(lambda x: x.get("createdon", None)),
        上门取件结束时间=df['FormattedValues'].apply(lambda x: x.get("new_pickupendon", None)),
        申请类别=df['FormattedValues'].apply(lambda x: x.get("new_applytype", None)),
        单号=df['new_name'],
        单据来源=df['FormattedValues'].apply(lambda x: x.get('new_fromsource', None)),
        省份=df['new_province_id'].apply(lambda x: x.get('name', None) if pd.notnull(x) else None)
    )
    #    # 选择需要的列
    df = df[[
        '单号', '创建时间', '上门取件结束时间', '申请类别', '单据来源', '省份'
    ]]

    return df


def getdata():
    pageindex = "1"
    url = generate_jxnrequrl(pageindex)
    rs = requests.get(url)
    count = rs.json()['Data']['TotalRecordCount']
    logger.info(f'未来即将到货量单据共{count}')
    datas = []

    for i in range(1, count // 5000 + 2):
        url = generate_jxnrequrl(str(i))
        data = fetch_api_data(url)
        logger.info(f"第{i}页数据已获取")
        datas.append(data)

    df = pd.concat(datas, ignore_index=True)

    df = extract_need_data(df)
    df.to_csv('tst.csv', index=False)
    return df


def make_sendgoods_data():
    data = getdata()
    data['上门取件结束时间'] = pd.to_datetime(data['上门取件结束时间'])
    data['创建时间'] = pd.to_datetime(data['创建时间'])
    data['月份'] = data['创建时间'].dt.month

    df = data.query("上门取件结束时间.notnull()").copy()
    df1 = data.query("单据来源 == '聚水潭' and 月份 !=12").copy()
    df = pd.concat([df, df1])

    df['取件至今'] = (pd.to_datetime('today') - df['上门取件结束时间']).dt.days
    df['取件天数'] = np.where(df['取件至今'] < 3, '0-3天内', np.where(df['取件至今'] < 7, '3-7天内',
                                                                      np.where(df['取件至今'] < 10, '7-10天内',
                                                                               '超10天')))
    df['月份'] = df['上门取件结束时间'].dt.month
    df = pd.merge(left=df, right=p_by_r, left_on='省份', right_on='省份')
    df = df.pivot_table(index=['取件天数', '地区', '省份'], values='单号', aggfunc='count')
    df = df.reset_index()
    df = df.rename(columns={'单号': '数量'})
    df = df.sort_values(['数量', '取件天数'], ascending=False)
    return df




