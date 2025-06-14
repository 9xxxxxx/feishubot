# -*- coding: utf-8 -*-
# @Time : 2025/4/11 17:17
# @Author : Garry-Host
# @FileName: sync_rtime_bidata_optimized.py
# @Software: PyCharm
import logging  # 确保导入 logging 模块
import hashlib
import math
import os
import time
import uuid
from datetime import datetime
from urllib.parse import quote

import pandas as pd
import requests
import schedule
import tenacity
from sqlalchemy import create_engine, exc
from sqlalchemy.pool import QueuePool

from asbot import AsBot
from my_utility import logger

# ======================== 配置信息 ========================
# 从环境变量读取敏感信息（建议通过docker/k8s配置）
DATABASE_URI = os.getenv("DATABASE_URI", "mysql+pymysql://root:000000@localhost/demo")
API_KEY = os.getenv("FS_API_KEY", "u7BDpKHA6VSqTScpEqZ4cPKmYVbQTAxgTBL2Gtit")
API_BASE_URL = os.getenv("API_BASE_URL", "https://ap6-openapi.fscloud.com.cn")

# ======================== 初始化组件 ========================
# 数据库引擎（带连接池）
engine = create_engine(
    DATABASE_URI,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600
)

# ======================== API客户端封装 ========================
class APIClient:
    def __init__(self, tenant="laifen"):
        self.tenant = tenant
        self.appid = "AS_department"
        self.queryid = "38c53a54-813f-a0e0-0000-06f40ebdeca5"

    def generate_url(self, pageindex: str, extend_conditions: str, page: int) -> str:
        """生成带签名的API请求URL"""
        timestamp = str(int(time.time() * 1000))
        reqid = str(uuid.uuid1())
        args = [
            self.appid,
            extend_conditions,
            "createdon descending",
            pageindex,
            "5000",  # pagesize
            "true",   # paging
            reqid,
            self.tenant,
            timestamp,
            "false",  # is_preview
            "true",   # is_user_query
            self.queryid,
            API_KEY
        ]

        # 生成签名
        sign_str = "".join(args)
        sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()

        # 编码特殊字符
        params = {
            "$tenant": quote(self.tenant),
            "$timestamp": quote(timestamp),
            "$reqid": quote(reqid),
            "$appid": quote(self.appid),
            "queryid": quote(self.queryid),
            "isUserQuery": "true",
            "isPreview": "false",
            "$pageindex": quote(pageindex),
            "$pagesize": "5000",
            "$paging": "true",
            "$extendConditions": quote(extend_conditions),
            "$orderby": quote("createdon descending"),
            "$sign": quote(sign)
        }

        url = f"{API_BASE_URL}/t/{self.tenant}/open/api/vlist/ExecuteQuery"
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        
        logger.info(f"Generated URL for page {page}: {url[:120]}...")  # 避免日志泄露完整URL
        return url

    @tenacity.retry(
        stop=tenacity.stop_after_attempt(3),
        wait=tenacity.wait_exponential(multiplier=1, min=2, max=10),
        retry=tenacity.retry_if_exception_type(requests.RequestException),
        before_sleep=tenacity.before_sleep_log(logger, logging.WARNING)  # 修复这里
    )
    def fetch_data(self, url: str, page: int) -> pd.DataFrame:
        """带重试机制的API请求"""
        try:
            response = requests.get(url, timeout=(3.05, 30))  # 连接超时3.05s，读取超时30s
            response.raise_for_status()
            
            data = response.json()
            if not data.get("Data") or "Entities" not in data["Data"]:
                raise ValueError("Invalid API response structure")
                
            df = pd.DataFrame(data["Data"]["Entities"])
            logger.info(f"Page {page} fetched successfully, records: {len(df)}")
            return df
            
        except Exception as e:
            logger.error(f"Failed to fetch page {page}: {str(e)}")
            raise

# ======================== 数据处理模块 ========================
class DataProcessor:
    @staticmethod
    def extract_fields(df: pd.DataFrame, identify: str) -> pd.DataFrame:
        """优化后的字段提取（向量化操作）"""
        # 使用str访问器优化嵌套字段提取
        data = pd.DataFrame()
        data = data.assign(
            产品类型=df["new_productmodel_id"].str.get("name"),
            产品名称=df["new_product_id"].str.get("name"),
            创建时间=df["FormattedValues"].str.get("createdon"),
            旧件签收时间=df["FormattedValues"].str.get("new_signedon"),
            检测时间=df["FormattedValues"].str.get("new_checkon"),
            申请类别=df["FormattedValues"].str.get("new_srv_rma_0.new_applytype"),
            一检时间=df["FormattedValues"].str.get("laifen_onechecktime"),
            维修完成时间=df["FormattedValues"].str.get("laifen_servicecompletetime"),
            质检完成时间=df["FormattedValues"].str.get("laifen_qualityrecordtime"),
            单号=df['new_rma_id'].str.get('name'),
            分拣人员=df['laifen_systemuser2_id'].str.get('name'),
            处理状态=df["FormattedValues"].str.get("new_srv_rma_0.new_status"),
            旧件处理状态=df["FormattedValues"].str.get("new_returnstatus"),
            检测结果=df["FormattedValues"].str.get("new_solution"),
            故障现象=df['new_error_id'].str.get('name'),
            发货时间=df["FormattedValues"].str.get("new_deliveriedon"),
            一检人员=df['laifen_systemuser_id'].str.get('name'),
            发货状态=df['FormattedValues'].str.get('new_srv_rma_0.new_deliverstatus'),
            产品序列号=df['new_userprofilesn'],
            服务人员=df['new_srv_workorder_1.new_srv_worker_id'].str.get('name'),
            单据来源=df["FormattedValues"].str.get("new_srv_rma_0.new_fromsource"),
            业务类型=identify
        )

        return data

# ======================== 核心业务逻辑 ========================
class SyncService:
    def __init__(self):
        self.api_client = APIClient()
        self.asbot = AsBot('人机黄乾')
    
    def get_sf_data(self, statu: str, identify: str) -> pd.DataFrame:
        """获取指定状态的数据"""
        logger.info(f"开始获取 {identify} 数据")
        
        # 初始请求获取总数
        extend_conditions = f'[{{"name":"{statu}","val":"2","op":"last-x-days"}}]'
        initial_url = self.api_client.generate_url("1", extend_conditions, 0)
        
        try:
            response = requests.get(initial_url, timeout=10)
            response.raise_for_status()
            count = response.json()['Data']['TotalRecordCount']
        except Exception as e:
            logger.error(f"获取总数失败: {str(e)}")
            raise
        
        total_pages = math.ceil(count / 5000)
        logger.info(f"Total pages: {total_pages}, Total records: {count}")
        
        # 分页获取数据
        dfs = []
        for page in range(1, total_pages + 1):
            try:
                url = self.api_client.generate_url(str(page), extend_conditions, page)
                df_page = self.api_client.fetch_data(url, page)
                dfs.append(df_page)
            except Exception as e:
                self.asbot.send_text_to_group(f"第{page}页数据获取失败，已跳过: {str(e)[:100]}")
                continue
                
        if not dfs:
            raise ValueError("所有分页请求均失败")
            
        df_combined = pd.concat(dfs, ignore_index=True)
        df_processed = DataProcessor.extract_fields(df_combined, identify)
        
        logger.info(f"成功处理 {len(df_processed)} 条{identify}数据")
        return df_processed
    
    def write_to_db(self, df: pd.DataFrame) -> int:
        """安全写入数据库"""
        try:
            with engine.connect() as conn:
                num = df.to_sql(
                    name='maintenance_ruiyun_realtime',
                    con=conn,
                    if_exists='replace',
                    index=False
                )
                conn.commit()
                return num
        except exc.SQLAlchemyError as e:
            logger.error(f"数据库写入失败: {str(e)}")
            self.asbot.send_text_to_group(f"数据库写入失败: {str(e)[:200]}")
            raise
    
    def get_rt_data(self):
        """主业务流程"""
        logger.info('开始执行数据同步任务')
        
        status_map = {
            "new_signedon": '签收',
            "new_checkon": '分拣',
            "laifen_servicecompletetime": '维修',
            "laifen_qualityrecordtime": '质检',
            "new_deliveriedon": '发货'
        }
        
        all_data = []
        for statu, identify in status_map.items():
            try:
                df = self.get_sf_data(statu, identify)
                all_data.append(df)
                self.asbot.send_text_to_group(f"{datetime.now()} 成功获取 {len(df)} 条{identify}数据")
            except Exception as e:
                logger.error(f"获取 {identify} 数据失败: {str(e)}")
                continue
                
        if not all_data:
            logger.warning("未获取到任何有效数据")
            return
            
        try:
            final_df = pd.concat(all_data, ignore_index=True)
            records_inserted = self.write_to_db(final_df)
            logger.info(f"成功写入 {records_inserted} 条数据")
            self.asbot.send_text_to_group(f"数据同步完成，本次插入{records_inserted}条记录")
        except Exception as e:
            logger.error(f"最终数据合并/写入失败: {str(e)}")

# ======================== 调度模块 ========================
def run_scheduler():
    """增强型调度器"""
    service = SyncService()
    service.get_rt_data()
    # 每日9-22点整点执行
    for hour in range(9, 23):
        schedule.every().day.at(f"{hour:02d}:00").do(safe_get_rt_data, service)
    
    # 心跳监测
    schedule.every(10).minutes.do(lambda: logger.info("Scheduler heartbeat"))
    
    while True:
        try:
            schedule.run_pending()
            sleep_time = 60 - datetime.now().second
            time.sleep(max(1, sleep_time))
        except KeyboardInterrupt:
            logger.warning("用户中断执行")
            break
        except Exception as e:
            logger.error(f"调度器异常: {str(e)}")
            time.sleep(60)

def safe_get_rt_data(service: SyncService):
    """带异常捕获的任务执行"""
    try:
        service.get_rt_data()
    except Exception as e:
        logger.error(f"任务执行失败: {str(e)}")
        service.asbot.send_text_to_group(f"任务异常: {str(e)[:200]}")

# ======================== Main ========================
if __name__ == "__main__":
    logger.info("Service starting...")
    run_scheduler()
    logger.info("Service shutdown gracefully")