from datetime import timedelta
import warnings
from data_process import *
from my_utility import *
from asbot import AsBot

from getdata import *
from config import asbot_config


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

    image_path1 = asbot_config.image_path1
    image_path2 = asbot_config.image_path2
    image_path3 = asbot_config.image_path3

    
    title1 = asbot_config.title1
    title2 = asbot_config.title2
    title3 = asbot_config.title3
    
    config_path = 'config/config.json'
    config = read_config(config_path)
    last_path = config['last_fp']


    # 获取发送寄修积压数据
    get_sf_data(path=path,days="1")
    data2send = make_jx_data(path=path, outpath=outpath, showdate=show_in_group,last_path=last_path)
    export_dataframe_to_image_v2(data2send, image_path1,title=title1)
    asbot.sendimage(image_path=image_path1)
    asbot.sendfile("xls", file_name=outfilename, file_path=outpath,type_file=type_file)

    # 获取发送快递量预测数据
    data2send0 = make_sendgoods_data()
    generate_asd_wc_image(data2send0,image_path2,title=title2)
    asbot.sendimage(image_path=image_path2)
    
    
    # 获取发送分拣数据
    dc_data = data_wait4check_and_detect(path=path)
    export_dataframe_to_image_for_normal(dc_data,image_path3,title=title3)
    asbot.sendimage(image_path=image_path3)
    
    config['last_fp'] = path
    write_config(config_path, config)
    
    logger.info("finishing Work&Work successfully~")
    logger.info(f'下次执行将在--{datetime.now() + timedelta(hours=2)}')
