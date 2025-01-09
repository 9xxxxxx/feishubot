import logging


logging.basicConfig(
    level=logging.INFO,  # 设置日志级别
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='../log/app.log',  # 日志文件名
    filemode='a',  # 追加模式
    encoding='utf-8",',
)

# 创建一个控制台输出处理器
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(console)  # 添加控制台处理器