import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os
from pathlib import Path

class VectorStore:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent.parent
        self.db_path = os.path.join(self.base_dir, "vector_db")
        
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # 创建或获取集合
        self.collection = self.client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # 初始化文本向量模型
        self.encoder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    def add_document(self, doc_id: str, content: str, metadata: dict):
        """添加文档到向量数据库"""
        # 生成文本向量
        embeddings = self.encoder.encode([content])
        
        # 添加到 ChromaDB
        self.collection.add(
            embeddings=[embeddings[0].tolist()],
            documents=[content],
            metadatas=[metadata],
            ids=[doc_id]
        )

    def semantic_search(self, query: str, limit: int = 5):
        """语义搜索"""
        query_embedding = self.encoder.encode(query)
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=limit
        )
        
        return results

vector_store = VectorStore()