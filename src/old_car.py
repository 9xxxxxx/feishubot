import json
import os
import time
import warnings
from datetime import datetime, timedelta
import pandas as pd
import requests
import xlwings as xw
from PIL import ImageGrab
from requests_toolbelt import MultipartEncoder
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import logging


logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log',  # 日志文件名
    filemode='a',  # 追加模式
    encoding='utf-8",',
)

# 创建一个控制台输出处理器
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(console)  # 添加控制台处理器

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


def uploadimage(path,token):
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

    msg = uploadimage(image_path,token)
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


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--window-size=1200,800')
    prefs = {'profile.default_content_settings.popups': 0,
             'download.default_directory': r"E:\Works\售后Bot\data\input"}
    options.add_experimental_option('prefs', prefs)
    # 你可以选择设置更多的浏览器选项
    driver = webdriver.Chrome(options=options)
    logger.info("初始化浏览器~")
    return driver


def login(driver, username, password):
    driver.get("https://ap6.fscloud.com.cn/t/laifen")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'username')))

    driver.find_element(By.ID, 'username').send_keys(username)
    driver.find_element(By.ID, 'password').send_keys(password)
    driver.find_element(By.ID, 'kc-login').click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="global-app"]/div/div/div[1]/div/div/div[2]/ul/li[3]/div')))
    logger.info("登录成功")


def navigate_to_page_and_download_data(driver, filename,day):
    # 点击逆向管理
    logger.info("正在下载瑞云寄修积压源文件~")
    time.sleep(2)
    driver.find_element(By.XPATH, '//*[@id="global-app"]/div/div/div[1]/div/div/div[2]/ul/li[3]/div/div[1]').click()
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="global-app"]/div/div/div[1]/div/div/div[2]/ul/li[3]/ul/li[2]')))

    # 点击服务单产品明细
    driver.find_element(By.XPATH, '//*[@id="global-app"]/div/div/div[1]/div/div/div[2]/ul/li[3]/ul/li[2]').click()

    time.sleep(2)
    # 点击自定义
    driver.find_element(By.XPATH, '//*[@id="tab-custom"]/span/span/button/span').click()
    time.sleep(2)
    # 点击模板
    driver.find_element(By.XPATH, '//div[@class="new_active" and @title="瑞云寄修积压"]/div').click()
    time.sleep(2)
    # 点击筛选
    driver.find_element(By.XPATH,
                        '//*[@id="__qiankun_microapp_wrapper_for_mainweb__"]/div[1]/div/div/div[1]/div[1]/div[1]/div[2]/div[2]/button[2]/span/span').click()
    time.sleep(2)
    # 设置旧件筛选天数
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-drawer__wrapper.rt-xpc-drawer.plat-advanced-filter > div > div > section > div.rt-list-filter.padding-size-bottom > div > div.rt-view-wrapper > form > div:nth-child(1) > div > div:nth-child(6) > div.el-form-item__content > div > div > input').send_keys(
        day)
    # 点击确定
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-drawer__wrapper.rt-xpc-drawer.plat-advanced-filter > div > div > section > div.rt-list-filter.padding-size-bottom > div > div.filter-btns-container > div > div > button.rt-button.rt-button--primary.rt-button--medium.rt-button--normal').click()
    time.sleep(1)
    # 设置文件名
    # 点击导出全部
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div:nth-child(12) > div > div > div.rt-view-wrapper > div.rt-header.rt-xpc-sticky.is-sticky > div.rt-plat-list-header-wrapper > div.rt-list-header > div > div.header-btns > div > div > div > button:nth-child(2) > span > span').click()
    # 设置文件名称
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-dialog__wrapper.excelExport-dialog.rt-dialog-wrapper.rt-dialog-normal > div > div.el-dialog__body > div > div > div > div > div.rc-section.rt-section.plat-section > div.section-body.rc-section-body > form > div.excelExport-card-form > div.el-row.is-align-top > div > div > div.el-form-item__content > div > div.el-input.rt-xpc-input > input').clear()
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-dialog__wrapper.excelExport-dialog.rt-dialog-wrapper.rt-dialog-normal > div > div.el-dialog__body > div > div > div > div > div.rc-section.rt-section.plat-section > div.section-body.rc-section-body > form > div.excelExport-card-form > div.el-row.is-align-top > div > div > div.el-form-item__content > div > div.el-input.rt-xpc-input > input').send_keys(
        filename)
    time.sleep(1)
    # 点击确定
    driver.find_element(By.CSS_SELECTOR,
                        '#__qiankun_microapp_wrapper_for_mainweb__ > div.el-dialog__wrapper.excelExport-dialog.rt-dialog-wrapper.rt-dialog-normal > div > div.el-dialog__body > div > div > div > div > div.plat-dialog-footer-buttons.has-border > button.rt-button.rt-button--primary.rt-button--medium.rt-button--normal > span > span').click()


    time.sleep(12)
    logger.info('源文件下载成功')
    driver.quit()


def extractinfo(path, outpath, showdate):
    logger.info(f'正在处理-{path}')
    df = pd.read_excel(path)
    myrows = df.query(" 发货状态.isnull() or 发货状态 == '待安排发货' ")
    rydf = myrows.query(" 申请类别 == '寄修/返修' ")
    data_0 = rydf.query("处理状态 != '已取消'")

    data = data_0.query("产品型号 == '产成品-电动牙刷' or 产品型号 == '产成品-吹风机'")

    tobedeliver = data.query(" 质检完成时间.notnull() and 发货时间.isnull() and 旧件处理状态 == '已质检'")
    tobefix = data.query("质检完成时间.isnull() and 维修完成时间.isnull()")
    tobeqc = data.query(" 维修完成时间.notnull() and 质检完成时间.isnull() and 旧件处理状态 == '已维修'")

    in_maintenance = tobefix.query(" 旧件处理状态 == '维修中'")
    checked = tobefix.query("旧件处理状态 == '已检测' ")
    first_Detected = tobefix.query(" 旧件处理状态 == '已一检'")
    Signed = tobefix.query(" 旧件处理状态 == '已签收'")
    first_Detected_exception = tobefix.query("旧件处理状态 == '一检异常'")
    checked_exception = tobefix.query("旧件处理状态 == '异常'")
    Exception_all = data.query("检测结果 == '异常'")

    with pd.ExcelWriter(outpath, engine='xlsxwriter') as writer:
        data.to_excel(writer, sheet_name='数据源', index=False)
        tobedeliver.to_excel(writer, sheet_name='待发货', index=False)
        tobeqc.to_excel(writer, sheet_name='待质检', index=False)

        tobefix.to_excel(writer, sheet_name='待维修', index=False)
        in_maintenance.to_excel(writer, sheet_name='待维修-维修中', index=False)
        first_Detected.to_excel(writer, sheet_name='待维修-已一检待派工', index=False)
        checked.to_excel(writer, sheet_name='待维修-已分拣待一检', index=False)
        Signed.to_excel(writer, sheet_name='待分拣-已签收待分拣', index=False)
        Exception_all.to_excel(writer, sheet_name='异常', index=False)

    dataall = data['单号'].shape[0]



    in_maintenance_all = in_maintenance['单号'].shape[0]
    first_Detected_all = first_Detected['单号'].shape[0]
    Signed_all = Signed['单号'].shape[0]
    checked_all = checked['单号'].shape[0]

    checked_exception_all = checked_exception['单号'].shape[0]
    first_Detected_exception_all = first_Detected_exception['单号'].shape[0]

    tobedeliver_dcf = tobedeliver.query('产品型号 == "产成品-吹风机"').shape[0]
    tobedeliver_ddys = tobedeliver.query('产品型号 == "产成品-电动牙刷"').shape[0]

    tobeqc_dcf = tobeqc.query('产品型号 == "产成品-吹风机"').shape[0]
    tobeqc_ddys = tobeqc.query('产品型号 == "产成品-电动牙刷"').shape[0]

    in_maintenance_dcf = in_maintenance.query('产品型号 == "产成品-吹风机"').shape[0]
    in_maintenance_ddys = in_maintenance.query('产品型号 == "产成品-电动牙刷"').shape[0]

    checked_dcf = checked.query('产品型号 == "产成品-吹风机"').shape[0]
    checked_ddys = checked.query('产品型号 == "产成品-电动牙刷"').shape[0]

    first_Detected_dcf = first_Detected.query('产品型号 == "产成品-吹风机"').shape[0]
    first_Detected_ddys = first_Detected.query('产品型号 == "产成品-电动牙刷"').shape[0]

    Signed_dcf = Signed.query('产品型号 == "产成品-吹风机"').shape[0]
    Signed_ddys = Signed.query('产品型号 == "产成品-电动牙刷"').shape[0]

    quantity = [tobedeliver_dcf,tobedeliver_ddys,
                tobeqc_dcf,tobeqc_ddys,
                in_maintenance_dcf, in_maintenance_ddys,
                first_Detected_dcf, first_Detected_ddys,
                checked_dcf, checked_ddys,
                Signed_dcf,Signed_ddys,
                checked_exception_all,first_Detected_exception_all]

    message = f"截止{showdate}，瑞云未发货共{dataall}台\n" \
              f"待发货：{tobedeliver_dcf + tobedeliver_ddys}台(吹风机{tobedeliver_dcf}台，电动牙刷{tobedeliver_ddys}台)\n" \
              f"待质检：{tobeqc_dcf + tobeqc_ddys}台(吹风机{tobeqc_dcf}台、电动牙刷{tobeqc_ddys}台)\n" \
              f"待维修：{checked_all + first_Detected_all + in_maintenance_all} (吹风机{checked_dcf + first_Detected_dcf + in_maintenance_dcf}、电动牙刷{checked_ddys + first_Detected_ddys + in_maintenance_ddys})\n" \
              f"\t已一检-待派工：{first_Detected_all}台 (吹风机{first_Detected_dcf}台、电动牙刷{first_Detected_ddys}台)\n" \
              f"\t已分检-待一检：{checked_all}台 (吹风机{checked_dcf}台、电动牙刷{checked_ddys}台)\n" \
              f"\t维修中：{in_maintenance_all}台(吹风机{in_maintenance_dcf}台、电动牙刷{in_maintenance_ddys}台)\n" \
              f"已签收-待分拣：{Signed_all}台 (吹风机{Signed_dcf}台、电动牙刷{Signed_ddys}台)\n" \
              f"异常：{checked_exception_all + first_Detected_exception_all}台 (分拣异常{checked_exception_all}台、一检异常{first_Detected_exception_all}台)\n" \
              f"具体清单如下，请查收"


    logger.info(message)
    logger.info(f'处理完成，文件保存至-{outpath}')
    return quantity


def makeimage(quanlity, path):
    # 打开 Excel 文件
    app = xw.App(visible=False, add_book=True)
    app.display_alerts = False  # 关闭一些提示信息，可以加快运行速度。 默认为 True。
    app.screen_updating = True
    wb = app.books[0]
    worksheet = wb.sheets['Sheet1']

    worksheet.range('A:A').column_width = 20  # 设置 A 列的宽度为 20
    worksheet.range('B:B').column_width = 20  # 设置 B 列的宽度为 30
    worksheet.range('C:C').column_width = 30
    worksheet.range('D:D').column_width = 20
    worksheet.range('1:16').row_height = 24  # 设置 A 列的宽度为 20
    worksheet.api.Cells.Font.Name = '微软雅黑'  # 设置字体为 Arial
    worksheet.api.Cells.Font.Size = 15  # 设置字体大小为 12
    worksheet.api.Cells.Font.Bold = True  # 设置字体为粗体
    worksheet.api.Cells.HorizontalAlignment = xw.constants.HAlign.xlHAlignCenter  # 水平居中对齐
    worksheet.api.Cells.VerticalAlignment = xw.constants.VAlign.xlVAlignCenter  # 垂直居中对齐
    columns_name = ['状态', '总计', datetime.now(), '数量', ]
    worksheet.range('A1').value = columns_name
    status = ['待发货', '待质检','待维修-维修中', '待维修-已一检', '待维修-已分拣', '待分拣-已签收', '异常', ]


    for i in range(0, len(quanlity)):
        worksheet.range(f'D{i + 2}').value = quanlity[i]

    i = 2
    for statu in status:
        worksheet.range(f'C{i}:C{i + 1}').options(transpose=True).value = ['电吹风', '电动牙刷']
        dwx = worksheet.range(f'A{i}:A{i + 1}')
        total = worksheet.range(f'B{i}:B{i + 1}')
        total.api.Merge()
        dwx.api.Merge()
        dwx.value = statu
        i = i + 2

    worksheet.range('B2').formula = '=SUM(D2:D3)'
    worksheet.range('B2:B15').api.FillDown()

    worksheet.range('2:2').api.Insert()  # 在第 2 行之前插入一行
    worksheet.range('A2').value = '总计'
    worksheet.range('B2').formula = '=SUM(D3:D16)'
    worksheet.range('B2:D2').api.Merge()
    worksheet.range('B2').font.color = '#FF0000'
    worksheet.range('A1:D1').color = '#00CCFF'

    # 截图
    rng = worksheet.range('A1:D16')
    rng.api.CopyPicture(Appearance=1, Format=2)  # 改进 CopyPicture 调用
    time.sleep(2)  # 延迟时间适当增加

    rng = worksheet.range('A1:D16')

    # 使用 list comprehension 来遍历每个单元格并清理内容
    for cell in rng:
        if cell.value:
            # 移除所有空格和回车符
            cleaned_value = ''.join(str(cell.value).split())
            cell.value = cleaned_value

    # 获取剪贴板图片
    img = ImageGrab.grabclipboard()

    if img is not None:
        img.save(path)  # 保存图片至本地
        logger.info(f"图片保存成功！保存至{path}")

    else:
        logger.info("截图失败，剪贴板内容为空。")

    # 退出 Excel
    wb.close()



def main(chat_name):
    logger.info("starting Work~")
    warnings.filterwarnings('ignore')

    showdate = datetime.now()
    showqz = showdate.strftime("%Y-%m-%d %H:%M")
    showdate = showdate.strftime("%Y-%m-%d %H-%M")

    filename = fr"瑞云积压数据{showdate}"
    outfilename = f"瑞云系统未发货清单截至{showdate}.xlsx"
    path = os.path.join("E:/Works/售后Bot/data/input/", filename) + '.xlsx'
    outpath = fr'E:/Works/售后Bot/data/output/{outfilename}'
    image_path = r'E:\Works\DataAnalysis\Source\data.jpeg'

    app_id = "cli_a7e1e09d72fe500e"
    app_secret = "sIsx3hT20I4oQ2lrq0ydAf04LTmaKxP7"
    type_file = "application/vnd.ms-excel"

    token = get_token(app_id=app_id,app_secret=app_secret)
    chat_id = get_chat_id(chat_name=chat_name,token=token)


    driver = init_driver()

    login(driver, 'huangqian', 'Laifen@2022')

    navigate_to_page_and_download_data(driver, filename=filename, day=5)

    quantity = extractinfo(path, outpath, showdate=showqz)

    makeimage(quantity,image_path)

    sendimage(image_path=image_path,token=token, chat_id=chat_id)

    sendfile("xls", file_name=outfilename, file_path=outpath,type_file=type_file, token=token, receive_id=chat_id)
    logger.info('执行成功')
    logger.info(f'下次执行将在--{datetime.now() + timedelta(hours=2)}')


if __name__ == '__main__':
    main('售后维修部')