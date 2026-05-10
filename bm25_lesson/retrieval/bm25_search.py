import jieba
from rank_bm25 import BM25L
import logging
# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BM25Search:
    def __init__(self, documents):
        # 初始化文档集合
        self.documents = documents
        # 分词后的文档
        self.tokenized_docs = [jieba.lcut(dec) for dec in documents]
        # 初始化BM25模型
        self.bm25 = BM25L(self.tokenized_docs)
        logger.info("BM25模型初始化完成")

    def search(self, query):
        # 分词查询
        tokenized_query = jieba.lcut(query)
        try:
            # 计算BM25得分
            scores = self.bm25.get_scores(tokenized_query)
            print(f"scores:{scores}" )
            # 获取得分最高的文档索引
            best_dix = scores.argmax()
            best_score = scores[best_dix]
            best_doc = self.documents[best_dix]
            logger.info(f"查询结果: {best_doc}, 最佳匹配:{best_doc},分数: {best_score}")
            return best_doc, best_score
        except Exception as e:
            logger.error(f"查询失败: {e}")
            return "查询失败"
if __name__ == "__main__":
    documents = [
        "这是一个关于机器学习的例子。",
        "这是一个关于深度学习的例子。",
        "这是一个关于自然语言处理的例子。",
        "这是一个关于计算机视觉的例子。",
        "这是一个关于图论的例子。",
        "这是一个关于概率论的例子。",
        "这是一个关于数据挖掘的例子。",
        "这是一个关于机器学习算法的例子。",
        "这是一个关于深度学习算法的例子。",
        "这是一个关于自然语言处理算法的例子。",
        "这是一个关于计算机视觉算法的例子。",
        "这是一个关于图论算法的例子. "]
    bm25S = BM25Search(documents)
    bm25S.search("关于机器学习的例子")