import warnings
from data_process import *
from my_utility import *
from asbot import AsBot
from getdata.get_checkgroup_efficiency import build_card_message
from getdata import *
from config import asbot_config

warnings.filterwarnings('ignore')
path = None

# 寄修积压
def send_sf_data(dp,days):
    global path
    logger.info("正在初始化机器人--开始发送寄修以及退换货数据")
    # 实例化机器人
    asbot = AsBot(dp)

    outfile_path = asbot_config.get_output_file_path()
    showdate = asbot_config.showdate()

    type_file = asbot_config.TYPE_FILE
    image_path1 = asbot_config.image_path1

    path = asbot_config.get_input_file_path()
    
    config_path = 'config/config.json'
    config = read_config(config_path)
    last_path = config['last_fp']


    # 获取发送寄修积压数据
    get_sf_data(path=path,days=days)
    data2send = make_jx_data(path=path, outpath=outfile_path, showdate= showdate,last_path=last_path)
    export_dataframe_to_image_v2(data2send, image_path1,title=asbot_config.get_jxjy_title1())
    asbot.sendimage(image_path=image_path1)
    time.sleep(1)
    asbot.sendfile("xls", file_name=asbot_config.get_send_file_name(), file_path=outfile_path,type_file=type_file)
    time.sleep(1)

    config['last_fp'] = path
    write_config(config_path, config)
    
    logger.info("寄修积压数据发送成功")


# 分拣积压
def send_returns_data(dp):
    data = get_sf_data()
    image_path3 = asbot_config.image_path3
    asbot = AsBot(dp)
    dc_data = data_wait4check_and_detect(data)
    export_dataframe_to_image_for_normal(dc_data,image_path3,title=asbot_config.get_fjjy_title2())
    asbot.sendimage(image_path=image_path3)
    time.sleep(1)
    logger.info("分拣一检积压数据发送成功")

# 快递物流预测
def sendgoods_data(dp):
    logger.info('发送快递量预测数据')
    # 实例化机器人
    asbot = AsBot(dp)
    
    image_path2 = asbot_config.image_path2

    # 获取发送快递量预测数据
    data2send0 = make_sendgoods_data()
    generate_asd_wc_image(data2send0,image_path2,title=asbot_config.get_wl_title3())
    asbot.sendimage(image_path=image_path2)
    time.sleep(1)
    logger.info('快递量预测数据发送成功')

# 手工创单量
def send_crm_data(dp):
    logger.info('发送一天内创单数据')
    # 实例化机器人
    asbot = AsBot(dp)

    image_path4 = asbot_config.image_path4

    # 获取发送快递量预测数据

    data = get_crm_data(path)
    make_crm_image(data,image_path4,asbot_config.get_crm_title4())
    asbot.sendimage(image_path=image_path4)
    time.sleep(1)
    logger.info('发送一天内创单数据成功')

# 分拣时效预警
def send_checkgroup_efficiency(dp):
    logger.info('发送当月以及当天分拣退换货时效数据')
    payload,condition = build_card_message()
    if condition < 0.85:
        asbot = AsBot(dp)
        asbot.send_card_to_group(payload)
        time.sleep(1)
        logger.info('发送当月以及当天分拣退换货时效数据成功')
    else:
        print(f'四小时内时效占比合格，为{round(condition,2)}%,达85%，不发送预警')

if __name__ == '__main__':
    # sendgoods_data('【售后维修部】吐槽群')
    send_returns_data('人机')