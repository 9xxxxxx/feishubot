from datetime import timedelta
import os
import warnings
from feishuapi import *
from data_process import *
from  download_data import *
from rwconfig import *
from get_sf_backlog import getdata
from get_sendgoods_data import make_sendgoods_data
from get_dc_data import data_wait4check_and_detect
from config.config import *


warnings.filterwarnings('ignore')

def make_data(path,outpath,showdate,last_path):
    latest_data = extractinfo(path, outpath, showdate)
    last_data = extractinfo_last(last_path)
    send_data = latest_data.copy()

    send_data['合计流转量'] = latest_data['合计'] - last_data['合计']
    send_data['牙刷流转量'] = latest_data['电动牙刷'] - last_data['电动牙刷']
    send_data['风机流转量'] = latest_data['电吹风'] - last_data['电吹风']

    send_data['合计流转量'] = send_data['合计流转量'].apply(lambda x: f"{'+' if x > 0 else ''}{x}")
    send_data['牙刷流转量'] = send_data['牙刷流转量'].apply(lambda x: f"{'+' if x > 0 else ''}{x}")
    send_data['风机流转量'] = send_data['风机流转量'].apply(lambda x: f"{'+' if x > 0 else ''}{x}")
    return send_data


def main(chat_name):
    logger.info("starting Work~")

    showdate = datetime.now()
    showqz = showdate.strftime("%Y-%m-%d %H:%M")
    showdate = showdate.strftime("%Y-%m-%d %H-%M")

    filename = fr"瑞云积压数据{showdate}"
    outfilename = f"瑞云系统未发货清单截至{showdate}.xlsx"
    path = os.path.join("E:/Works/售后Bot/data/input/", filename) + '.xlsx'
    outpath = fr'E:/Works/售后Bot/data/output/{outfilename}'

    image_path = r'E:\Works\售后Bot\data\image\data.png'
    image_path2 = r'E:\Works\售后Bot\data\image\data0.png'
    image_path3 = r'E:\Works\售后Bot\data\image\data1.png'
    
    title1 = f'寄修数据实时汇报--{showqz}'
    title2 = f'快递单时效分布4到货量预估--{showqz}'
    title3 = f'退换货分拣数据实时汇报--{showqz}'
    
    config_path = '../config/config.json'
    config = read_config(config_path)
    last_path = config['last_fp']
    app_id = config['app_id']
    app_secret = config['app_secret']
    type_file = config['type_file']

    token = get_token(app_id=app_id,app_secret=app_secret)
    chat_id = get_chat_id(chat_name=chat_name,token=token)

    # driver = init_driver()

    # login(driver, 'huangqian', 'Laifen@2022')

    # navigate_to_page_and_download_data(driver, filename=filename, day=15)
    
    # 获取发送寄修积压数据
    getdata(path=path,days="15")
    data2send = make_data(path=path, outpath=outpath, showdate=showdate,last_path=last_path)
    export_dataframe_to_image_v2(data2send, image_path,title=title1)
    sendimage(image_path=image_path,token=token, chat_id=chat_id)
    sendfile("xls", file_name=outfilename, file_path=outpath,type_file=type_file, token=token, receive_id=chat_id)

    # 获取发送快递量预测数据
    # data2send0 = make_sendgoods_data()
    # export_dataframe_to_image_for_normal(data2send0,image_path2,title=title2)
    # sendimage(image_path=image_path2, token=token,chat_id=chat_id)
    
    
    # 获取发送分拣数据
    dc_data = data_wait4check_and_detect(path=path)
    export_dataframe_to_image_for_normal(dc_data,image_path3,title=title3)
    sendimage(image_path=image_path3,token=token,chat_id=chat_id)
    
    
    config['last_fp'] = path
    write_config(config_path, config)
    
    logger.info("finishing Work&Work successfully~")
    logger.info(f'下次执行将在--{datetime.now() + timedelta(hours=2)}')
