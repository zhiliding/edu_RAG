"""
优化版Markdown智能切分器
支持学科/项目层级结构：学科 > 项目 > 文档
"""
import re
import os
from typing import List, Dict, Tuple
from langchain.docstore.document import Document
from datetime import datetime


class OptimizedMarkdownSplitter:
    """优化的MD文档智能切分器 - 支持学科/项目层级"""

    def __init__(self,
                 max_chunk_size: int = 2000,
                 min_chunk_size: int = 100,
                 overlap: int = 50):
        """
        初始化参数

        Args:
            max_chunk_size: 单个chunk的最大字符数
            min_chunk_size: 单个chunk的最小字符数
            overlap: 相邻chunk之间的重叠字符数
        """
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
        self.overlap = overlap
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)

    def split_document(self, doc: Document, subject: str, project: str) -> List[Document]:
        """
        智能切分MD文档

        Args:
            doc: 原始文档
            subject: 学科标识（如'ai', 'java'）
            project: 项目标识（如'kg', 'edurag', 'subject_intro'）

        Returns:
            切分后的Document列表
        """
        content = doc.page_content
        file_path = doc.metadata.get("file_path", "")

        # 1. 解析文档结构树
        doc_tree = self._parse_document_tree(content)

        # 2. 识别文档类型
        doc_type = self._infer_document_type(content, doc_tree, file_path)

        # 3. 递归切分为语义chunk
        chunks = []
        self._recursive_split(doc_tree, chunks, file_path, subject, project, doc_type)

        return chunks

    def _parse_document_tree(self, content: str) -> Dict:
        """解析MD文档的层级树结构"""
        lines = content.split('\n')
        root = {
            'level': 0,
            'title': 'root',
            'content': '',
            'children': [],
            'start_line': 0,
            'end_line': len(lines)
        }

        stack = [root]
        current_node = root
        content_buffer = []

        for i, line in enumerate(lines):
            heading_match = self.heading_pattern.match(line)

            if heading_match:
                # 保存上一个节点的内容
                if content_buffer:
                    current_node['content'] = '\n'.join(content_buffer).strip()
                    content_buffer = []

                # 创建新节点
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()

                new_node = {
                    'level': level,
                    'title': title,
                    'content': '',
                    'children': [],
                    'start_line': i,
                    'end_line': i
                }

                # 找到合适的父节点
                while stack and stack[-1]['level'] >= level:
                    stack.pop()

                parent = stack[-1] if stack else root
                parent['children'].append(new_node)

                stack.append(new_node)
                current_node = new_node
            else:
                content_buffer.append(line)

        # 保存最后一个节点的内容
        if content_buffer:
            current_node['content'] = '\n'.join(content_buffer).strip()

        return root

    def _infer_document_type(self, content: str, tree: Dict, file_path: str) -> str:
        """
        推断文档类型

        Returns:
            文档类型：project_intro/course_outline/technical_doc/tutorial/general
        """
        # 从文件名判断
        filename = os.path.basename(file_path).lower()

        if '简介' in filename or 'intro' in filename or '项目背景' in content[:500]:
            return 'project_intro'

        if '课程大纲' in content or '整体内容目录' in content:
            return 'course_outline'

        if '安装' in content or '使用方法' in content or '代码示例' in content:
            return 'technical_doc'

        if '学习目标' in content or '教程' in filename:
            return 'tutorial'

        return 'general'

    def _recursive_split(self, node: Dict, chunks: List[Document],
                         file_path: str, subject: str, project: str, doc_type: str,
                         parent_path: str = ""):
        """递归切分节点为chunk"""
        # 构建当前节点的完整路径
        current_path = f"{parent_path} > {node['title']}" if parent_path else node['title']

        # 计算当前节点的完整内容
        full_content = self._build_node_content(node)
        content_length = len(full_content)

        # 策略1: 内容适中，直接作为一个chunk
        if self.min_chunk_size <= content_length <= self.max_chunk_size:
            chunk = self._create_chunk(
                content=full_content,
                title=node['title'],
                level=node['level'],
                path=current_path,
                file_path=file_path,
                subject=subject,
                project=project,
                doc_type=doc_type
            )
            chunks.append(chunk)

        # 策略2: 内容过长，递归切分子节点
        elif content_length > self.max_chunk_size and node['children']:
            # 创建概要chunk
            summary_content = self._build_summary_content(node)
            if len(summary_content) >= self.min_chunk_size:
                summary_chunk = self._create_chunk(
                    content=summary_content,
                    title=f"{node['title']}（概述）",
                    level=node['level'],
                    path=current_path,
                    file_path=file_path,
                    subject=subject,
                    project=project,
                    doc_type=doc_type,
                    is_summary=True
                )
                chunks.append(summary_chunk)

            # 递归处理子节点
            for child in node['children']:
                self._recursive_split(child, chunks, file_path, subject,
                                      project, doc_type, current_path)

        # 策略3: 无子节点但内容过长，强制切分
        elif content_length > self.max_chunk_size and not node['children']:
            sub_chunks = self._force_split_long_content(
                content=full_content,
                title=node['title'],
                level=node['level'],
                path=current_path,
                file_path=file_path,
                subject=subject,
                project=project,
                doc_type=doc_type
            )
            chunks.extend(sub_chunks)

        # 策略4: 内容太短但仍然保留
        elif content_length > 0:
            chunk = self._create_chunk(
                content=full_content,
                title=node['title'],
                level=node['level'],
                path=current_path,
                file_path=file_path,
                subject=subject,
                project=project,
                doc_type=doc_type
            )
            chunks.append(chunk)

    def _build_node_content(self, node: Dict) -> str:
        """构建节点的完整内容（包含标题、内容、子节点）"""
        if node['level'] == 0:
            return node['content']

        parts = [f"{'#' * node['level']} {node['title']}"]

        if node['content']:
            parts.append(node['content'])

        for child in node['children']:
            child_content = self._build_node_content(child)
            if child_content:
                parts.append(child_content)

        return '\n\n'.join(parts)

    def _build_summary_content(self, node: Dict) -> str:
        """构建节点的概要内容（不包含子节点）"""
        if node['level'] == 0:
            return node['content']

        parts = [f"{'#' * node['level']} {node['title']}"]

        if node['content']:
            parts.append(node['content'])

        return '\n\n'.join(parts)

    def _force_split_long_content(self, content: str, title: str, level: int,
                                  path: str, file_path: str, subject: str,
                                  project: str, doc_type: str) -> List[Document]:
        """强制切分过长的内容"""
        chunks = []
        paragraphs = content.split('\n\n')

        current_chunk = []
        current_size = 0
        part_num = 1

        for para in paragraphs:
            para_size = len(para)

            if current_size + para_size > self.max_chunk_size and current_chunk:
                chunk_content = '\n\n'.join(current_chunk)
                chunk = self._create_chunk(
                    content=chunk_content,
                    title=f"{title}（第{part_num}部分）",
                    level=level,
                    path=path,
                    file_path=file_path,
                    subject=subject,
                    project=project,
                    doc_type=doc_type
                )
                chunks.append(chunk)

                overlap_text = current_chunk[-1] if current_chunk else ""
                current_chunk = [overlap_text, para] if overlap_text else [para]
                current_size = len(overlap_text) + para_size
                part_num += 1
            else:
                current_chunk.append(para)
                current_size += para_size

        if current_chunk:
            chunk_content = '\n\n'.join(current_chunk)
            chunk = self._create_chunk(
                content=chunk_content,
                title=f"{title}（第{part_num}部分）" if part_num > 1 else title,
                level=level,
                path=path,
                file_path=file_path,
                subject=subject,
                project=project,
                doc_type=doc_type
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk(self, content: str, title: str, level: int, path: str,
                      file_path: str, subject: str, project: str, doc_type: str,
                      is_summary: bool = False) -> Document:
        """创建Document chunk"""
        keywords = self._extract_keywords(content)

        return Document(
            page_content=content,
            metadata={
                "file_path": file_path,
                "timestamp": datetime.now().isoformat(),
                # ===== 核心层级字段 =====
                "subject": subject,  # 学科：ai/java/ops
                "project": project,  # 项目：kg/edurag/subject_intro
                "doc_type": doc_type,  # 文档类型
                # ===== 结构字段 =====
                "title": title,
                "level": level,
                "section_path": path,
                "is_summary": is_summary,
                # ===== 辅助字段 =====
                "keywords": keywords,
                "chunk_size": len(content)
            }
        )

    def _extract_keywords(self, content: str, top_n: int = 10) -> List[str]:
        """提取内容关键词"""
        clean_content = re.sub(r'[#*`\[\]()]', '', content)
        words = re.findall(r'[\u4e00-\u9fa5a-zA-Z]{2,}', clean_content)

        from collections import Counter
        word_freq = Counter(words)

        return [word for word, _ in word_freq.most_common(top_n)]


# ===== 使用示例 =====
if __name__ == "__main__":
    # 示例：知识图谱项目简介
    kg_intro_doc = Document(
        page_content="""
## 知识图谱项目背景介绍

### 学习目标
* 了解项目的开发背景.
* 了解知识图谱的相关基础概念.

### 项目背景
* 知识图谱（Knowledge Graph）是人工智能的重要分支技术...
* 传智教育的AI引领IT教育前沿, 特此推出关于娱乐领域的知识图谱项目...
        """,
        metadata={"file_path": "ai_data/kg_data/1-项目简介.md"}
    )

    # 示例：学科介绍
    subject_intro_doc = Document(
        page_content="""
# 人工智能就业课 【课程大纲】

整体内容目录：
第一部分：大模型语言基础
第二部分：大模型语言进阶
第三部分：数据处理与统计分析

## 第一部分：大模型语言基础
### 可解决的现实问题
熟练掌握Python语言...
        """,
        metadata={"file_path": "/Users/ligang/PycharmProjects/LLM/EduRAG_system/rag_qa/data/ai_data/人工智能就业课课程大纲.md"}
    )

    splitter = OptimizedMarkdownSplitter(
        max_chunk_size=1500,
        min_chunk_size=100
    )

    # 测试切分
    print("=" * 60)
    print("测试1: 知识图谱项目文档")
    print("=" * 60)
    kg_chunks = splitter.split_document(kg_intro_doc, subject='ai', project='kg')
    for i, chunk in enumerate(kg_chunks, 1):
        print(f"\nChunk {i}:")
        print(f"  学科: {chunk.metadata['subject']}")
        print(f"  项目: {chunk.metadata['project']}")
        print(f"  标题: {chunk.metadata['title']}")
        print(f"  类型: {chunk.metadata['doc_type']}")
        print(f"  路径: {chunk.metadata['section_path']}")
        print(f"  内容: {chunk.page_content[:100]}...\n")

    print("\n" + "=" * 60)
    print("测试2: 学科介绍文档")
    print("=" * 60)
    intro_chunks = splitter.split_document(subject_intro_doc, subject='ai', project='subject_intro')
    for i, chunk in enumerate(intro_chunks, 1):
        print(f"\nChunk {i}:")
        print(f"  学科: {chunk.metadata['subject']}")
        print(f"  项目: {chunk.metadata['project']}")
        print(f"  标题: {chunk.metadata['title']}")
        print(f"  内容: {chunk.page_content[:100]}...")