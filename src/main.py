from datetime import timedelta
import warnings
from data_process import *
from my_utility import *
from asbot import AsBot

from getdata import *
from config import asbot_config


warnings.filterwarnings('ignore')

def sf_and_returns_data(dp):
    logger.info("发送寄修以及分拣一检积压数据")
    # 实例化机器人
    asbot = AsBot(dp)

    show_in_group = asbot_config.show_in_group
    outfilename = asbot_config.outfilename
    path = asbot_config.path
    outpath = asbot_config.outpath
    type_file = asbot_config.TYPE_FILE

    image_path1 = asbot_config.image_path1
    image_path2 = asbot_config.image_path2


    title1 = asbot_config.title1
    title2 = asbot_config.title2

    
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
    
    
    config['last_fp'] = path
    write_config(config_path, config)
    
    logger.info("寄修以及分拣一检积压数据发送成功")

    
    
def sendgoods_data(dp):
    logger.info('发送快递量预测数据')
    # 实例化机器人
    asbot = AsBot(dp)
    image_path2 = asbot_config.image_path2

    title2 = asbot_config.title2

    # 获取发送快递量预测数据
    data2send0 = make_sendgoods_data()
    generate_asd_wc_image(data2send0,image_path2,title=title2)
    asbot.sendimage(image_path=image_path2)
    logger.info('快递量预测数据发送成功')