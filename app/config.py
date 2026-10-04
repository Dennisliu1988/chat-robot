# 配置管理（读取 .env）
from dotenv import load_dotenv  # 从 python-dotenv 导入：把 .env 文件加载进环境变量

load_dotenv()  # 读取项目根目录的 .env，把里面的键值写入进程环境变量