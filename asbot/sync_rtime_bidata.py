# -*- coding: utf-8 -*-
# @Time : 2025/4/11 17:17
# @Author : Garry-Host
# @FileName: sync_rtime_bidata.py
# @Software: PyCharm
import hashlib
import time
import uuid
from datetime import datetime, time as dt_time
import schedule
from sqlalchemy import create_engine
import requests
import pandas as pd
from asbot import AsBot
from my_utility import logger

conn = create_engine("mysql+pymysql://root:000000@localhost/demo", pool_pre_ping=True,  # 每次从连接池获取连接前会检查连接是否有效
    pool_recycle=3600)
    

# 获取寄修数据积压数据

def generate_requrl(pageindex, extendConditions, page):
    logger.info(f"正在生成第{page}页的URL")
    """
    从 API 获取数据并转换为 DataFrame
    """
    # 基本参数
    tenant = "laifen"
    api_name = "api/vlist/ExecuteQuery"
    timestamp = str(int(time.time() * 1000))
    reqid = str(uuid.uuid1())
    appid = "AS_department"
    queryid = "38c53a54-813f-a0e0-0000-06f40ebdeca5"
    is_user_query = "true"
    is_preview = "false"
    pagesize = "5000"
    paging = "true"
    key = "u7BDpKHA6VSqTScpEqZ4cPKmYVbQTAxgTBL2Gtit"
    orderby = "createdon descending"
    args = [appid, extendConditions, orderby, pageindex, pagesize, paging, reqid, tenant, timestamp, is_preview,
            is_user_query, queryid, key]

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
        f"&$extendConditions={extendConditions}&$orderby={orderby}&$sign={sign}"
    )
    logger.info(f"成功生成第{page}页的URL: {url}")
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


def extract_need_data(df, identifiy):
    df = df.assign(
        产品类型=df["new_productmodel_id"].apply(lambda x: x.get('name', None) if pd.notnull(x) else None),
        产品名称=df["new_product_id"].apply(lambda x: x.get('name', None) if pd.notnull(x) else None),
        创建时间=df["FormattedValues"].apply(lambda x: x.get("createdon", None)),
        旧件签收时间=df["FormattedValues"].apply(lambda x: x.get("new_signedon", None)),
        检测时间=df["FormattedValues"].apply(lambda x: x.get("new_checkon", None)),
        申请类别=df["FormattedValues"].apply(lambda x: x.get("new_srv_rma_0.new_applytype", None)),
        一检时间=df["FormattedValues"].apply(lambda x: x.get("laifen_onechecktime", None)),
        维修完成时间=df["FormattedValues"].apply(lambda x: x.get("laifen_servicecompletetime", None)),
        质检完成时间=df["FormattedValues"].apply(lambda x: x.get("laifen_qualityrecordtime", None)),
        单号=df['new_rma_id'].apply(lambda x: x.get('name', None)),
        分拣人员=df['laifen_systemuser2_id'].apply(lambda x: x.get('name', None) if pd.notnull(x) else None),
        处理状态=df["FormattedValues"].apply(lambda x: x.get("new_srv_rma_0.new_status", None)),
        旧件处理状态=df["FormattedValues"].apply(lambda x: x.get("new_returnstatus", None)),
        检测结果=df["FormattedValues"].apply(lambda x: x.get("new_solution", None)),
        故障现象=df['new_error_id'].apply(lambda x: x.get('name', None) if pd.notnull(x) else None),
        发货时间=df["FormattedValues"].apply(lambda x: x.get("new_deliveriedon", None)),
        一检人员=df['laifen_systemuser_id'].apply(lambda x: x.get('name', None) if pd.notnull(x) else None),
        发货状态=df['FormattedValues'].apply(lambda x: x.get('new_srv_rma_0.new_deliverstatus', None)),
        产品序列号=df['new_userprofilesn'],
        服务人员=df['new_srv_workorder_1.new_srv_worker_id'].apply(
            lambda x: x.get('name', None) if pd.notnull(x) else None),
        单据来源=df["FormattedValues"].apply(lambda x: x.get("new_srv_rma_0.new_fromsource", None)),
        业务类型=identifiy
    )
    #    # 选择需要的列
    df = df[[
        '单号', '产品类型', '产品名称', '处理状态', '旧件处理状态', '检测结果', '申请类别', '旧件签收时间',
        '检测时间', '一检时间', '维修完成时间', '质检完成时间', '故障现象', '发货时间', '发货状态',
        '一检人员', '产品序列号', '分拣人员', '服务人员', '单据来源', '创建时间', '业务类型'
    ]]
    logger.info(f"成功提取所需数据,共{df.shape[1]}列")
    return df


def get_sf_data(statu, identifiy):
    logger.info(f"正在下载最近2天的{identifiy}数据")
    pageindex = "1"
    extendConditions = f'[{{"name":"{statu}","val":"2","op":"last-x-days"}}]'
    url = generate_requrl(pageindex, extendConditions, '0')
    rs = requests.get(url)
    count = rs.json()['Data']['TotalRecordCount']
    logger.info(f"最近2天{identifiy}业务量共{count}单,共{count // 5000 + 2}页数据")
    datas = []

    for i in range(1, count // 5000 + 2):
        url = generate_requrl(str(i), extendConditions, i)
        data = fetch_api_data(url, i)
        logger.info(f"第{i}页数据已获取")
        datas.append(data)

    df = pd.concat(datas, ignore_index=True)
    df = extract_need_data(df, identifiy)

    logger.info(f"已成功下载最近2天的{identifiy}数据")
    return df


def get_rt_data():
    logger.info('开干')
    status = {"new_signedon": '签收', "new_checkon": '分拣', "laifen_servicecompletetime": '维修',
              "laifen_qualityrecordtime": '质检', "new_deliveriedon": '发货'}
    datas = []
    for statu, identify in status.items():
        data = get_sf_data(statu, identify)
        datas.append(data)
        logger.info(f'成功下载{data.shape[0]}条{identify}数据')
        asbot = AsBot('人机黄乾')
        asbot.send_text_to_group(f'{datetime.now()}成功插入{data.shape[0]}条{identify}数据')
        logger.info(f"成功插入{data.shape[0]}{identify}条数据")
    data = pd.concat(datas, ignore_index=True)
    num = data.to_sql('maintenance_ruiyun_realtime', conn, if_exists='replace', index=False)
    logger.info(f"OK啦，已经是成功存储了{num}条数据")
    logger.info(f"执行获取数据操作，当前时间: {datetime.now().strftime('%H:%M:%S')}")


def run_scheduler():
    # 设置9-22点每小时任务
    for hour in range(9, 23):
        schedule.every().day.at(f"{hour:02d}:00").do(get_rt_data)

    try:
        while True:
            now = datetime.now()
            # 动态休眠：距离下次整点的剩余秒数（最多休眠60秒）
            sleep_seconds = 60 - now.second
            schedule.run_pending()
            time.sleep(min(60, max(1, sleep_seconds)))  # 保证1-60秒
    except KeyboardInterrupt:
        logger.info("程序已停止")

if __name__ == "__main__":
    get_rt_data()
    logger.info('lets go')
    run_scheduler()