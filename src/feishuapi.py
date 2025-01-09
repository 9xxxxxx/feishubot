import requests
from requests_toolbelt import MultipartEncoder
import json
from log import logger


def get_token(app_id, app_secret):
    url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal'
    data = {
        "Content-Type": "application/json; charset=utf-8",
        "app_id": app_id,
        "app_secret": app_secret
    }
    response = requests.request("POST", url, data=data)
    logger.info("获取bearer token")
    return json.loads(response.text)['tenant_access_token']

# 获取  receive_id
def get_chat_id(chat_name,token):
    url = "https://open.feishu.cn/open-apis/im/v1/chats?page_size=20"
    payload = ''

    Authorization = 'Bearer ' + token
    headers = {
        'Authorization': Authorization
    }
    response = requests.request("GET", url, headers=headers, data=payload)
    items = json.loads(response.text)['data']['items']
    for item in items:
        if item['name'] == chat_name:
            logger.info(f"获取{chat_name}的chat_id")
            return item['chat_id']

def get_filekey(file_type, file_name, file_path,type_file,token):
    url = "https://open.feishu.cn/open-apis/im/v1/files"
    form = {'file_type': file_type,
            'file_name': file_name,
            'file': (file_name, open(file_path, 'rb'), type_file)}
    multi_form = MultipartEncoder(form)
    Authorization = 'Bearer ' + token
    headers = {'Authorization': Authorization, 'Content-Type': multi_form.content_type}
    response = requests.request("POST", url, headers=headers, data=multi_form)
    logger.info(f"上传文件获取file_key")
    if response.status_code == 200:
        logger.info("获取file_key成功")
    return json.loads(response.content)['data']['file_key']

def get_imagekey(path,token):
    url = "https://open.feishu.cn/open-apis/im/v1/images"
    form = {'image_type': 'message',
            'image': (open(path, 'rb'))}  # 需要替换具体的path
    multi_form = MultipartEncoder(form)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': multi_form.content_type}
    response = requests.request("POST", url, headers=headers, data=multi_form)
    decoded_string = response.content.decode('utf-8')
    image_key = json.loads(decoded_string)['data']['image_key']
    logger.info("上传图片获取image_key")
    if response.status_code == 200:
        logger.info("获取image_key成功")
    return image_key

def sendimage(image_path,token,chat_id):

    msg = get_imagekey(image_path,token)
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type":"chat_id"}
    msgContent = {
        "image_key": msg,
    }

    req = {
        "receive_id": chat_id, # chat id
        "msg_type": "image",
        "content": json.dumps(msgContent)
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': f'Bearer {token}', # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    logger.info("正在发送图片~")
    if response.status_code == 200:
        logger.info("发送图片成功！")

# 发送文件
def sendfile(file_type, file_name, file_path,type_file, token,receive_id):
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"}

    file_key = get_filekey(file_type, file_name, file_path,type_file,token=token)

    msgContent = {
        "file_key": file_key,
    }

    req = {
        "receive_id": receive_id,
        "msg_type": "file",
        "content": json.dumps(msgContent)
    }
    payload = json.dumps(req)
    Authorization = 'Bearer ' + token
    headers = {
        'Authorization': Authorization,
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    logger.info("正在发送文件~")
    if response.status_code == 200:
        logger.info("发送文件成功")

def sendtext(msg,chat_id,token):

    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "chat_id"}
    msgContent = {
        "text": msg,
    }

    req = {
        "receive_id": chat_id,  # chat id
        "msg_type": "text",
        "content": json.dumps(msgContent)
    }
    payload = json.dumps(req)
    headers = {
        'Authorization': f'Bearer {token}',  # your access token
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, params=params, headers=headers, data=payload)
    print(response.status_code)  # Print Response