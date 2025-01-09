import hashlib
import time
import uuid
from urllib.parse import quote

import requests

pageindex = "1"
conditions = '{"new_signedon":"5"}'

def generate_requrl(pageindex,conditions):

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
    additionalConditions = quote(conditions, safe='')

    args = [conditions, appid, orderby, pageindex, pagesize, paging, reqid, tenant, timestamp, is_preview, is_user_query, queryid, key]
    
    """
    生成签名
    """
    
    sign_str = "".join(args)
    sign = hashlib.sha256(sign_str.encode('utf-8')).hexdigest().upper()
    #构建 URL
    url = (
        f"https://ap6-openapi.fscloud.com.cn/t/{tenant}/open/{api_name}"
        f"?$tenant={tenant}&$timestamp={timestamp}&$reqid={reqid}&$appid={appid}"
        f"&queryid={queryid}&isUserQuery={is_user_query}&isPreview={is_preview}"
        f"&$pageindex={pageindex}&$pagesize={pagesize}&$paging={paging}"
        f"&$additionalConditions={additionalConditions}&$orderby={orderby}&$sign={sign}"
    )

    return url

url = generate_requrl(pageindex,conditions)
print(url)
