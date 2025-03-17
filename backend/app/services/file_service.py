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
        print(f"内容长度: {len(content)} 字符")
        
        ix = open_dir(self.index_dir)
        with ix.writer() as writer:
            writer.delete_by_term('file_path', file_path)
            writer.add_document(
                file_path=file_path,
                filename=os.path.basename(file_path),
                content=content
            )

    def search(self, query_string: str, limit: int = 10) -> List[dict]:
        ix = open_dir(self.index_dir)
        with ix.searcher() as searcher:
            # 打印索引内容
            print("当前索引中的所有文档:")
            for doc in searcher.all_stored_fields():
                print(f"- {doc['filename']}: {doc['content'][:100]}...")
            
            # 使用 OrGroup 来匹配任意字段
            filename_query = QueryParser("filename", ix.schema, group=OrGroup).parse(query_string)
            content_query = QueryParser("content", ix.schema, group=OrGroup).parse(query_string)
            
            # 分别搜索文件名和内容
            filename_results = searcher.search(filename_query, limit=limit)
            content_results = searcher.search(content_query, limit=limit)
            
            # 合并结果并去重
            seen = set()
            results = []
            
            for r in filename_results:
                if r["file_path"] not in seen:
                    seen.add(r["file_path"])
                    results.append({
                        "file_path": r["file_path"],
                        "filename": r["filename"],
                        "content": r["content"],
                        "score": r.score,
                        "match_type": "filename"
                    })
            
            for r in content_results:
                if r["file_path"] not in seen:
                    seen.add(r["file_path"])
                    results.append({
                        "file_path": r["file_path"],
                        "filename": r["filename"],
                        "content": r["content"],
                        "score": r.score,
                        "match_type": "content"
                    })
            
            # 按相关度排序
            results.sort(key=lambda x: x["score"], reverse=True)
            return results[:limit]

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
    query = "光子嫩肤3次卡，现金"
    print(f"搜索查询: {query}")
    results = fs.search(query)
    print(f"搜索结果数量: {len(results)}")
    for r in results:
        print("\n---")
        print(f"文件: {r['filename']}")
        print(f"相关度: {r['score']}")
        print(f"匹配类型: {r['match_type']}")