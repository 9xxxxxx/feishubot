import requests
import time
import uuid
import hashlib
import pandas as pd
from my_utility import logger
import json
from datetime import datetime, timedelta, UTC
from sqlalchemy import create_engine

conn = create_engine("mysql+pymysql://root:000000@localhost/demo")


def generate_requrl(pageindex):
    logger.info(f"正在生成第{pageindex}页的URL")
    """
    从 API 获取数据并转换为 DataFrame
    """
    # 基本参数
    tenant = "laifen"
    api_name = "api/vlist/ExecuteQuery"
    timestamp = str(int(time.time() * 1000))
    reqid = str(uuid.uuid1())
    appid = "AS_department"
    queryid = "cf4c2854-813f-a095-0000-06ffe67a4b77"
    is_user_query = "true"
    is_preview = "false"
    pagesize = "5000"
    paging = "true"
    key = "u7BDpKHA6VSqTScpEqZ4cPKmYVbQTAxgTBL2Gtit"
    # orderby = "createdon descending"
    # extendConditions = quote([{"name":"new_checkon","val":"this-month","op":"this-month"}], safe='')
    # additionalConditions = quote({"createdon":"","new_signedon":"","new_checkon":"","laifen_qualityrecordtime":"","laifen_servicecompletetime":""}, safe='')
    # extendConditions = '[{"name":"createdon","val":["2025-01-01T00:00:00.000Z","2025-01-03T00:00:00.000Z"],"op":"between"}]'
    extendConditions = get_time_interverl_condition()

    args = [appid, extendConditions, pageindex, pagesize, paging, reqid, tenant, timestamp, is_preview, is_user_query,
            queryid, key]

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
        f"&$extendConditions={extendConditions}&$sign={sign}"
    )
    logger.info(f"成功生成第{pageindex}页的URL: {url}")
    return url


def fetch_api_data(url, page):
    logger.info(f"正在获取第{page}页数据")
    # 发送 GET 请求
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"API 请求失败，状态码: {response.status_code}")

    # 解析 JSON 数据
    data = response.json()
    entities = data["Data"]["Entities"]
    df = pd.DataFrame(entities)
    logger.info(f"第{page}页数据，已通过API获取成功获取")
    return df


def extract_need_data(df):
    api_data = pd.DataFrame()
    api_data = api_data.assign(
        服务单=df['new_workorder_id'].apply(lambda x: x.get("name", None) if pd.notnull(x) else None),
        创建时间=df["FormattedValues"].apply(lambda x: x.get("createdon", None)),
        质检结果=df['FormattedValues'].apply(lambda x: x.get("new_result", None)),
        负责人=df['ownerid'].apply(lambda x: x.get("name", None) if pd.notnull(x) else None),
        服务人员=df['new_srv_workorder_0.new_srv_worker_id'].apply(
            lambda x: x.get('name', None) if pd.notnull(x) else None),
        产品类别=df['laifen_productgroup_id'].apply(lambda x: x.get("name", None) if pd.notnull(x) else None),
        故障现象=df['new_srv_workorder_0.laifen_error_id'].apply(
            lambda x: x.get("name", None) if pd.notnull(x) else None),
        质检说明=df['new_memo'].apply(lambda x: x if pd.notnull(x) else None),
    )
    #    # 选择需要的列

    logger.info(f"成功提取所需数据,共{api_data.shape[1]}列")
    return api_data


def get_qcrecord_data():
    logger.info(f"正在下载质检的数据")
    url = generate_requrl("1")
    rs = requests.get(url)
    print(rs.text)
    count = rs.json()['Data']['TotalRecordCount']
    logger.info(f"当天质检数量共{count}单,共{count // 5000 + 2}页数据")
    datas = []

    for i in range(1, count // 5000 + 2):
        url = generate_requrl(str(i))
        data = fetch_api_data(url, i)
        logger.info(f"第{i}页数据已获取")
        datas.append(data)

    df = pd.concat(datas, ignore_index=True)
    df = extract_need_data(df)
    logger.info(f"已成功下载当月数据")
    return df


# 获取当前日期
def get_time_interverl_condition():
    current_date = datetime.now(UTC).replace(hour=0, minute=0, second=0, microsecond=0)

    # 计算起始日期（当前日期减去一天）
    start_date = current_date - timedelta(days=1)

    # 格式化为ISO 8601格式，包含时区信息
    start_iso = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso = current_date.strftime("%Y-%m-%dT%H:%M:%SZ")

    # 构造JSON对象
    json_obj = [{
        "name": "createdon",
        "val": [start_iso, end_iso],
        "op": "between"
    }]

    # 生成JSON字符串
    json_str = json.dumps(json_obj)

    return json_str

def sync_qcrecord_data():
    qcdata = get_cg_efficiency_data()
    qcdata.to_sql('qc_record', conn, if_exists='append', index=False)