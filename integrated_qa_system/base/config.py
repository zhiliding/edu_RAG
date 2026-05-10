# base/config.py
# 导入配置解析库
import configparser
# 导入路径操作库
import os
current_path = os.path.dirname(os.path.abspath(__file__))
parent_path = os.path.dirname(current_path)
config_file = os.path.join(parent_path, 'config.ini')



class Config:
    # 初始化配置，加载 config.ini 文件
    def __init__(self, config_file=config_file):
        # 创建配置解析器
        self.config = configparser.ConfigParser()
        # 读取配置文件
        self.config.read(config_file)

        # MySQL 配置
        # MySQL 主机地址
        self.MYSQL_HOST = self.config.get('mysql', 'host', fallback='localhost')
        # MySQL 用户名
        self.MYSQL_USER = self.config.get('mysql', 'user', fallback='root')
        # MySQL 密码
        self.MYSQL_PASSWORD = self.config.get('mysql', 'password', fallback='123456')
        # MySQL 数据库名
        self.MYSQL_DATABASE = self.config.get('mysql', 'database', fallback='subjects_kg')

        # Redis 配置
        # Redis 主机地址
        self.REDIS_HOST = self.config.get('redis', 'host', fallback='localhost')
        # Redis 端口
        self.REDIS_PORT = self.config.getint('redis', 'port', fallback=6379)
        # Redis 密码
        self.REDIS_PASSWORD = self.config.get('redis', 'password', fallback='1234')
        # Redis 数据库编号
        self.REDIS_DB = self.config.getint('redis', 'db', fallback=0)
        # 日志文件路径
        self.LOG_FILE = self.config.get('logger', 'log_file', fallback='logs/app.log')

if __name__ == '__main__':
    conf = Config()
    print(conf.MYSQL_PASSWORD)
