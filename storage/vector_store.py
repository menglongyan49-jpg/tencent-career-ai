"""
向量数据库模块
用于知识库检索
"""
from typing import List, Dict, Any, Optional
from pathlib import Path


class VectorStore:
    """向量数据库封装"""

    def __init__(self, persist_dir: str = "./data/chroma"):
        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = None
        self._collection = None

    def _get_client(self):
        """延迟初始化 ChromaDB 客户端"""
        if self._client is None:
            try:
                import chromadb
                self._client = chromadb.PersistentClient(path=str(self.persist_dir))
            except ImportError:
                print("Warning: chromadb not installed, using fallback storage")
        return self._client

    def _get_collection(self, name: str = "knowledge"):
        """获取或创建集合"""
        client = self._get_client()
        if client is None:
            return None
        return client.get_or_create_collection(name=name)

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ):
        """添加文档"""
        collection = self._get_collection()
        if collection is None:
            return

        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]

        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )

    def query(
        self,
        query_text: str,
        n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """查询相似文档"""
        collection = self._get_collection()
        if collection is None:
            return []

        results = collection.query(
            query_texts=[query_text],
            n_results=n_results,
        )

        # 格式化结果
        documents = []
        for i, doc in enumerate(results.get("documents", [[]])[0]):
            documents.append({
                "content": doc,
                "metadata": results.get("metadatas", [[]])[0][i] if results.get("metadatas") else {},
                "distance": results.get("distances", [[]])[0][i] if results.get("distances") else None,
            })

        return documents

    def count(self) -> int:
        """获取文档数量"""
        collection = self._get_collection()
        if collection is None:
            return 0
        return collection.count()