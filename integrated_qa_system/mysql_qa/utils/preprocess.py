# utils/preprocess.py
# 导入分词库
import jieba
# 导入日志
from integrated_qa_system.base import logger

def preprocess_text(text):
    # 预处理文本
    logger.info("开始预处理文本")
    try:
        # 分词并转换为小写
        return jieba.lcut(text.lower())
    except AttributeError as e:
        # 记录预处理失败
        logger.error(f"文本预处理失败: {e}")
        # 返回空列表
        return []

if __name__ == "__main__":
    # 测试预处理函数

    print(preprocess_text("天下相亲与相爱,动身千里外 心自成一脉,今夜万家灯火时,或许隔窗望 梦中佳境在."))