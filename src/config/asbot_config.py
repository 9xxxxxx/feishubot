from datetime import datetime
import os


# 数据库配置
DATABASE = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "000000",
    "database": "demo"
}
# dialect+driver://username:password@host:port/database

DB_STRING = rf'mysql+pymysql://{DATABASE['user']}:{DATABASE['password']}@{DATABASE['host']}:{DATABASE['port']}/{DATABASE['database']}'
# API 配置
APP_ID = "cli_a7e1e09d72fe500e"
APP_SECRET = "sIsx3hT20I4oQ2lrq0ydAf04LTmaKxP7"


# 
LAST_FP = "E:/Works/售后Bot/data/input/瑞云积压数据2025-01-14 10-11.xlsx"
TYPE_FILE = "application/vnd.ms-excel"


# 日期配置
date = datetime.now()
show_in_group = date.strftime("%Y-%m-%d %H:%M")
showdate = date.strftime("%Y-%m-%d %H-%M")


# 文件路径配置
filename = fr"瑞云积压数据{showdate}"
outfilename = f"瑞云系统未发货清单截至{showdate}.xlsx"
path = os.path.join("E:/Works/售后Bot/data/input/", filename) + '.xlsx'
outpath = fr'E:/Works/售后Bot/data/output/{outfilename}'


# 文件路径
image_path1 = r'..\data\image\data.png'
image_path2 = r'..\data\image\data0.png'
image_path3 = r'..\data\image\data1.png'


# 标题
title1 = f'寄修数据实时汇报--{show_in_group}'
title2 = f'物流单分布实时汇报--{show_in_group}'
title3 = f'退换货分拣数据实时汇报--{show_in_group}'
# print(DB_STRING)