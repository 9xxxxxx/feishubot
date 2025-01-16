from datetime import timedelta
import warnings
from src.data_process import *
from my_utility import *
from getdata.get_sf_backlog_data import getdata
from getdata.get_dc_data import data_wait4check_and_detect
from asbot import AsBot
import config.asbot_config as asbot_config

warnings.filterwarnings('ignore')

def main():
    logger.info("starting Work~")
    # 实例化机器人
    asbot = AsBot('人机')

    show_in_group = asbot_config.show_in_group
    outfilename = asbot_config.outfilename
    path = asbot_config.path
    outpath = asbot_config.outpath
    type_file = asbot_config.TYPE_FILE

    image_path = asbot_config.image_path
    image_path2 = asbot_config.image_path2
    image_path3 = asbot_config.image_path3
    
    title1 = asbot_config.title1
    title2 = asbot_config.title2
    title3 = asbot_config.title3
    
    config_path = '../config/config.json'
    config = read_config(config_path)
    last_path = config['last_fp']


    # 获取发送寄修积压数据
    getdata(path=path,days="1")
    data2send = make_jx_data(path=path, outpath=outpath, showdate=show_in_group,last_path=last_path)
    export_dataframe_to_image_v2(data2send, image_path,title=title1)
    asbot.sendimage(image_path=image_path)
    asbot.sendfile("xls", file_name=outfilename, file_path=outpath,type_file=type_file)

    # 获取发送快递量预测数据
    # data2send0 = make_sendgoods_data()
    # export_dataframe_to_image_for_normal(data2send0,image_path2,title=title2)
    # sendimage(image_path=image_path2, token=token,chat_id=chat_id)
    
    
    # 获取发送分拣数据
    dc_data = data_wait4check_and_detect(path=path)
    export_dataframe_to_image_for_normal(dc_data,image_path3,title=title3)
    asbot.sendimage(image_path=image_path3)
    
    config['last_fp'] = path
    write_config(config_path, config)
    
    logger.info("finishing Work&Work successfully~")
    logger.info(f'下次执行将在--{datetime.now() + timedelta(hours=2)}')
