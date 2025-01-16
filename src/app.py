from main import main, logger
import schedule
import time
from datetime import datetime, timedelta


class TaskScheduler:
    def __init__(self):
        """初始化任务调度器"""
        self.schedule = schedule


    def job(self, department="售后维修部"):
        """需要执行的任务"""
        main()
        logger.info(f"任务执行时间: {datetime.now()}")

        # 如果是 8:00 运行的任务，安排下一次任务在 2 小时后
        if datetime.now().time() == datetime.strptime("08:00", "%H:%M").time():
            next_run_time = datetime.now() + timedelta(hours=2)
            self.schedule.clear()  # 清除所有已安排的任务
            self.schedule.every().day.at(next_run_time.strftime("%H:%M")).do(self.job)
            self.schedule_jobs()  # 重新安排其他任务

    def is_time_between(self, start_time, end_time):
        """检查当前时间是否在指定时间范围内"""
        now = datetime.now().time()
        return start_time <= now <= end_time

    def run_job_if_time_allowed(self):
        """在允许的时间范围内运行任务"""
        if not self.is_time_between(datetime.strptime("22:01", "%H:%M").time(), datetime.strptime("07:59", "%H:%M").time()):
            self.job()

    def print_scheduled_jobs(self):
        """打印所有计划任务"""
        print("当前计划任务：")
        for job in self.schedule.jobs:
            print(f"- 任务: {job.job_func.__name__}, 下次运行时间: {job.next_run}")

    def schedule_jobs(self):
        """安排任务"""
        # 每天 8:00 运行一次
        self.schedule.every().day.at("08:00").do(self.job)

        # 每两个小时运行一次，但跳过 22:00 点
        for hour in range(10, 22, 2):  # 从 10 点到 20 点，每两小时一次
            self.schedule.every().day.at(f"{hour:02d}:00").do(self.run_job_if_time_allowed)

        # 每天 22:00 运行最后一次
        self.schedule.every().day.at("22:00").do(self.job)

    def run(self):
        """启动任务调度器"""
        # 启动时立即运行一次
        self.job()

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
