from main import sendgoods_data,sf_and_returns_data,send_crm_data
from my_utility import logger
import schedule
import time
from datetime import datetime


class TaskScheduler:
    def __init__(self):
        """初始化任务调度器"""
        self.schedule = schedule
        self.department = "售后维修部"
        self.days = "10"


    def job1(self):
        """在允许的时间范围内运行任务"""
        sf_and_returns_data(self.department,self.days)
        logger.info(f"任务job执行时间: {datetime.now()}")
    
    def job2(self):
        sendgoods_data(self.department)
        logger.info(f"任务job2执行时间: {datetime.now()}")

    def job3(self):
        send_crm_data(self.department)
        logger.info(f"任务job3执行时间: {datetime.now()}")

    def print_scheduled_jobs(self):
        """打印所有计划任务"""
        print("当前计划任务：")
        for job in self.schedule.jobs:
            print(f"- 任务: {job.job_func.__name__}, 运行时间: {job.next_run}")

    def schedule_jobs(self):
        """安排任务"""
        # 每天 8:00 运行一次
        self.schedule.every().day.at("08:00").do(self.job1)

        self.schedule.every().day.at("13:30").do(self.job1)

        self.schedule.every().day.at("18:00").do(self.job1)


        # # 每两个小时运行一次，但跳过 22:00 点
        # for hour in range(10, 22, 2):  # 从 10 点到 20 点，每两小时一次
        #     self.schedule.every().day.at(f"{hour:02d}:00").do(self.job1)
        

        # 每天 9:00 和 17:00 运行 job2
        self.schedule.every().day.at("09:00").do(self.job2)
        self.schedule.every().day.at("17:00").do(self.job2)


        # 每天 9:00 运行job3
        # self.schedule.every().day.at("09:00").do(self.job3)

    def run(self):
        """启动任务调度器"""
        # 启动时立即运行一次
        self.job1()
        # self.job2()
        # self.job3()

        # 安排任务
        self.schedule_jobs()
        self.print_scheduled_jobs()

        # 保持程序运行
        while True:
            self.schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    scheduler = TaskScheduler()
    scheduler.run()
