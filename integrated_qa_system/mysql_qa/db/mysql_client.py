# 导入 MySQL 连接库
import pymysql
# 导入pandas
import pandas as pd
# 导入配置和日志
import os, sys


from integrated_qa_system.base import Config, logger

class MySQLClient:
    def __init__(self):
        # 初始化日志
        self.logger = logger
        try:
            # 连接 MySQL 数据库
            self.connection = pymysql.connect(
                host=Config().MYSQL_HOST,
                user=Config().MYSQL_USER,
                password=Config().MYSQL_PASSWORD,
                database=Config().MYSQL_DATABASE,
                charset="utf8mb4",
            )
            # 创建游标
            self.cursor = self.connection.cursor()
            # 记录连接成功
            self.logger.info("MySQL 连接成功")
        except pymysql.MySQLError as e:
            # 记录连接失败
            self.logger.error(f"MySQL 连接失败: {e}")
            raise

    def ensure_alive(self):
        """空闲过久后 MySQL 会断开，执行 SQL 前先保活/重连"""
        try:
            self.connection.ping(reconnect=True)
        except pymysql.MySQLError as e:
            self.logger.warning(f"MySQL 重连: {e}")
            self.connection = pymysql.connect(
                host=Config().MYSQL_HOST,
                user=Config().MYSQL_USER,
                password=Config().MYSQL_PASSWORD,
                database=Config().MYSQL_DATABASE,
                charset="utf8mb4",
            )
            self.cursor = self.connection.cursor()

    def create_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS JP_wenda (
            id INT AUTO_INCREMENT PRIMARY KEY,
            subject_name VARCHAR(20),
            question VARCHAR(1000),
            answer VARCHAR(1000)
        );"""

        try:
            self.cursor.execute(create_table_query)
            self.connection.commit()
            self.logger.info("创建表成功")
        except pymysql.MySQLError as e:
            self.logger.error(f"创建表失败: {e}")
            raise

    def insert_data(self, csv_path):
        try:
            data = pd.read_csv(csv_path)
            for _, row in data.iterrows():
                insert_query = "INSERT INTO JP_wenda (subject_name, question, answer) VALUES (%s, %s, %s)"
                self.cursor.execute(insert_query, (row['学科名称'], row['问题'], row['答案']))
            self.connection.commit()
            self.logger.info("数据插入成功")
        except Exception as e:
            self.logger.error(f"数据插入失败: {e}")
            self.connection.rollback()
            raise

    def fetch_question(self):
        # 回去所有问题
        try:
            # 执行查询
            self.cursor.execute("SELECT question FROM JP_wenda")
            # 获取结果
            results = self.cursor.fetchall()
            # 记录获取成功
            self.logger.info("获取所有问题成功")
            # 返回结果
            return results
        except Exception as e:
            # 记录获取失败
            self.logger.error(f"获取所有问题失败: {e}")
            raise

    def fetch_answer(self, question):
        # 获取指定问题的答案
        try:
            # 执行查询
            self.cursor.execute("SELECT answer FROM JP_wenda WHERE question=%s", (question,))
            # 获取结果
            result = self.cursor.fetchone()
            # 返回答案或 None
            return result[0] if result else None
        except pymysql.MySQLError as e:
            # 记录答案获取失败
            self.logger.error(f"答案获取失败: {e}")
            # 返回 None
            return None

    def close(self):
        # 关闭数据库连接
        try:
            # 关闭连接
            self.connection.close()
            # 记录关闭成功
            self.logger.info("MySQL 连接已关闭")
        except pymysql.MySQLError as e:
            # 记录关闭失败
            self.logger.error(f"关闭连接失败: {e}")

if __name__ == "__main__":
    # 创建 MySQL 客户端
    client = MySQLClient()
    # client.create_table()
    # client.insert_data("D:\\biji\\AI_LLM\\edu_rag_project\\integrated_qa_system\\mysql_qa\\data\\JP学科知识问答.csv")
    print(client.fetch_question())
    print(client.fetch_answer("用上下文管理器实现函数运行时间的计算?"))