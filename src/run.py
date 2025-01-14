import schedule
from datetime import datetime
from datetime import time
import time as t2s
from old_car import main


def job():
    current_time = datetime.now().time()

    if time(9, 50) <= current_time <= time(22, 9):  # 假设你想在 10:00 到 12:00 之间不执行任务
        print("执行任务")
        main('售后维修部')
    else:
        print("当前时间在 22:11 到 7:49 之间，跳过任务")



schedule.every().day.at("07:50").do(job)
# 每两个小时执行一次任务
schedule.every(2).hours.do(job)

# 主循环
while True:
    schedule.run_pending()
    t2s.sleep(1)  # 确保每次检查间隔至少一秒，避免 CPU 占用过高