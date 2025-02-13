import subprocess
import time
import schedule
def job_kill_server():
    try:
        # 运行 PowerShell 命令
        result = subprocess.run(
            ["powershell", "-Command", "Stop-Process -Name Rscript"],
            capture_output=True,
            text=True,
        )

        # 输出结果
        print("标准输出:", result.stdout)
        print("标准错误:", result.stderr)
        print("返回码:", result.returncode)

        # 检查返回码
        if result.returncode != 0:
            print("脚本执行失败，请检查错误信息。")
        else:
            print("脚本执行成功。")

    except subprocess.TimeoutExpired:
        print("脚本执行超时")
    except Exception as e:
        print("发生异常:", str(e))


def job_start_server():
    try:

        # 运行 PowerShell 命令
        result = subprocess.run(
            ["powershell", "-Command", r"Rscript.exe E:\Dev\AS_Bot\asbot\script\app.R"],
            capture_output=True,
            text=True,
        )

        # 输出结果
        print("标准输出:", result.stdout)
        print("标准错误:", result.stderr)
        print("返回码:", result.returncode)
        print(result)
        # 检查返回码
        if result.returncode != 0:
            print("脚本执行失败，请检查错误信息。")
        else:
            print("脚本执行成功。")

    except subprocess.TimeoutExpired:
        print("脚本执行超时")
    except Exception as e:
        print("发生异常:", str(e))



schedule.every().day.at("07:20").do(job_kill_server)
schedule.every().day.at("07:30").do(job_start_server)
while True:
    schedule.run_pending()
    time.sleep(1)
