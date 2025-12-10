from typing import List, Optional

from langchain_pinecone import PineconeVectorStore
from langchain_core.documents import Document   # ✅ new location
from pinecone import Pinecone, ServerlessSpec

from llm_models.llm_models import embeddings_model
from config.config import Config
import time
import uuid


class PineconeVectorDB:
    
    def __init__(self, index_name: str = None):
        self.index_name = index_name or Config.PINECONE_INDEX_NAME
        self.embeddings = embeddings_model
        self.pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        self._ensure_index_exists()
        self.vector_store = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings
        )
    
    def _ensure_index_exists(self):
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            self.pc.create_index(
                name=self.index_name,
                dimension=3072,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
            while not self.pc.describe_index(self.index_name).status['ready']:
                time.sleep(1)
    
    def add_documents(self, documents: List[Document], namespace: str = "") -> List[str]:
        ids = self.vector_store.add_documents(documents=documents, namespace=namespace)
        return ids
    
    def similarity_search(self, query: str, k: int = 5, namespace: str = "", filter: Optional[dict] = None) -> List[Document]:
        return self.vector_store.similarity_search(query=query, k=k, namespace=namespace, filter=filter)
    
    def delete_index(self):
        self.pc.delete_index(self.index_name)
    
    def get_index_stats(self) -> dict:
        index = self.pc.Index(self.index_name)
        return index.describe_index_stats()
    
    @staticmethod
    def list_all_indexes() -> List[dict]:
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        indexes = []
        for index in pc.list_indexes():
            indexes.append({
                "name": index.name,
                "dimension": index.dimension,
                "metric": index.metric,
                "host": index.host
            })
        return indexes
    
    @staticmethod
    def delete_index_by_name(index_name: str):
        pc = Pinecone(api_key=Config.PINECONE_API_KEY)
        pc.delete_index(index_name)
    
    @staticmethod
    def generate_unique_index_name() -> str:
        return f"quiz-{uuid.uuid4().hex[:8]}"
