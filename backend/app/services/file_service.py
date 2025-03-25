import os
from typing import List, Dict
from fastapi import UploadFile
from whoosh.index import create_in, open_dir
from whoosh.fields import Schema, TEXT, ID, STORED
from whoosh.qparser import QueryParser, OrGroup
from pypdf import PdfReader
from docx import Document
from datetime import datetime
import shutil
from jieba.analyse import ChineseAnalyzer  # 添加中文分词支持
from pathlib import Path
from app.services.vector_store import vector_store
import uuid

class FileService:
    def __init__(self):
        # 获取backend目录的路径
        self.base_dir = Path(__file__).parent.parent.parent
        # 设置索引和上传目录的路径
        self.index_dir = os.path.join(self.base_dir, "file_index")
        self.upload_dir = os.path.join(self.base_dir, "uploads")
        self._ensure_dirs()
        self._init_index()

    def _ensure_dirs(self):
        # 确保目录存在
        for dir_path in [self.index_dir, self.upload_dir]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                print(f"创建目录: {dir_path}")
            else:
                print(f"目录已存在: {dir_path}")

    def _init_index(self):
        # 使用中文分词器
        analyzer = ChineseAnalyzer()
        schema = Schema(
            file_path=ID(stored=True),
            filename=TEXT(stored=True, analyzer=analyzer),  # 使用中文分词
            content=TEXT(stored=True, analyzer=analyzer)    # 使用中文分词
        )
        
        # 如果索引目录不存在或强制重建
        if not os.path.exists(os.path.join(self.index_dir, "MAIN")):
            if os.path.exists(self.index_dir):
                shutil.rmtree(self.index_dir)
            os.makedirs(self.index_dir)
            create_in(self.index_dir, schema)

    async def save_file(self, file: UploadFile) -> str:
        file_path = os.path.join(self.upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 提取文件内容并建立索引
        content = self._extract_content(file_path)
        self._index_document(file_path, content)
        
        return file_path

    def _extract_content(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext in ['.doc', '.docx']:
            return self._extract_docx(file_path)
        return ""

    def _extract_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        return " ".join(page.extract_text() for page in reader.pages)

    def _extract_docx(self, file_path: str) -> str:
        doc = Document(file_path)
        return " ".join(paragraph.text for paragraph in doc.paragraphs)

    def _index_document(self, file_path: str, content: str):
        print(f"正在创建索引: {os.path.basename(file_path)}")
        
        # 创建全文索引
        ix = open_dir(self.index_dir)
        with ix.writer() as writer:
            writer.delete_by_term('file_path', file_path)
            writer.add_document(
                file_path=file_path,
                filename=os.path.basename(file_path),
                content=content
            )
        
        # 添加到向量数据库
        doc_id = str(uuid.uuid4())
        vector_store.add_document(
            doc_id=doc_id,
            content=content,
            metadata={
                'file_path': file_path,
                'filename': os.path.basename(file_path)
            }
        )

    def search(self, query_string: str, limit: int = 10, search_type: str = "hybrid") -> List[dict]:
        results = []
        
        if search_type in ["hybrid", "fulltext"]:
            # 全文搜索结果
            fulltext_results = self._fulltext_search(query_string, limit)
            results.extend(fulltext_results)
            
        if search_type in ["hybrid", "semantic"]:
            # 语义搜索结果
            semantic_results = self._semantic_search(query_string, limit)
            results.extend(semantic_results)
            
        # 去重并按相关度排序
        unique_results = self._deduplicate_results(results)
        return sorted(unique_results, key=lambda x: x["score"], reverse=True)[:limit]

    def _fulltext_search(self, query_string: str, limit: int) -> List[dict]:
        # 原有的全文搜索逻辑
        ix = open_dir(self.index_dir)
        with ix.searcher() as searcher:
            # 使用 MultifieldParser 支持多字段搜索
            from whoosh.qparser import MultifieldParser
            multifield_parser = MultifieldParser(["filename", "content"], ix.schema, group=OrGroup)
            multifield_query = multifield_parser.parse(query_string)
            
            # 创建高亮器
            from whoosh.highlight import Highlighter, ContextFragmenter, HtmlFormatter
            formatter = HtmlFormatter(tagname="mark", classname="search-highlight")
            fragmenter = ContextFragmenter(maxchars=300, surround=50)
            highlighter = Highlighter(fragmenter=fragmenter, formatter=formatter)
            
            # 获取搜索结果
            results = searcher.search(multifield_query, limit=limit)
            
            search_results = []
            for hit in results:
                # 使用高亮器处理内容
                content_highlights = highlighter.highlight_hit(
                    hit, "content",
                    text=hit.get("content", "")
                )
                filename_highlights = highlighter.highlight_hit(
                    hit, "filename",
                    text=hit.get("filename", "")
                )
                
                search_results.append({
                    "file_path": hit["file_path"],
                    "filename": filename_highlights or hit["filename"],
                    "content": content_highlights or hit["content"][:300],
                    "score": hit.score,
                    "match_type": "content" if content_highlights else "filename"
                })
            
            return search_results

    def _semantic_search(self, query_string: str, limit: int) -> List[dict]:
        results = vector_store.semantic_search(query_string, limit)
        
        search_results = []
        for idx, (doc, score, metadata) in enumerate(zip(
            results['documents'][0],
            results['distances'][0],
            results['metadatas'][0]
        )):
            search_results.append({
                "file_path": metadata["file_path"],
                "filename": metadata["filename"],
                "content": doc[:300],  # 截取前300个字符
                "score": 1 - score,  # 转换距离为相似度分数
                "match_type": "semantic"
            })
        
        return search_results

    def _deduplicate_results(self, results: List[dict]) -> List[dict]:
        seen = set()
        unique_results = []
        
        for result in results:
            file_path = result["file_path"]
            if file_path not in seen:
                seen.add(file_path)
                unique_results.append(result)
        
        return unique_results

    def get_file_list(self, page: int = 1, page_size: int = 10) -> Dict:
        """获取已上传的文件列表"""
        all_files = []
        for filename in os.listdir(self.upload_dir):
            file_path = os.path.join(self.upload_dir, filename)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                all_files.append({
                    "filename": filename,
                    "size": file_stat.st_size,
                    "upload_time": datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "file_type": os.path.splitext(filename)[1][1:].upper()
                })
        
        # 排序和分页
        all_files.sort(key=lambda x: x["upload_time"], reverse=True)
        total = len(all_files)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        return {
            "total": total,
            "items": all_files[start_idx:end_idx]
        }

    def rebuild_index(self):
        """重建所有文档的索引"""
        print(f"开始重建索引，上传目录: {self.upload_dir}")
        # 删除旧索引
        if os.path.exists(self.index_dir):
            shutil.rmtree(self.index_dir)
            print(f"删除旧索引目录: {self.index_dir}")
        
        # 重新初始化索引
        self._init_index()
        print("初始化新索引完成")
        
        # 重新索引所有文档
        file_count = 0
        for filename in os.listdir(self.upload_dir):
            file_path = os.path.join(self.upload_dir, filename)
            if os.path.isfile(file_path):
                print(f"正在索引文件: {filename}")
                content = self._extract_content(file_path)
                self._index_document(file_path, content)
                file_count += 1
        
        print(f"索引重建完成，共处理 {file_count} 个文件")

if __name__ == "__main__":
    fs = FileService()
    print("\n=== 开始测试 ===")
    print(f"上传目录: {fs.upload_dir}")
    print(f"索引目录: {fs.index_dir}")
    
    # 重建索引
    print("\n=== 重建索引 ===")
    fs.rebuild_index()
    
    # 测试搜索
    print("\n=== 测试搜索 ===")
    query = "工作报告"
    print(f"搜索查询: {query}")
    results = fs.search(query)
    print(f"搜索结果数量: {len(results)}")
    for r in results:
        print("\n---")
        print(f"文件: {r['filename']}")
        print(f"相关度: {r['score']}")
        print(f"匹配类型: {r['match_type']}")