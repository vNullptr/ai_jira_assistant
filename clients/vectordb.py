from pydantic import BaseModel, Field, computed_field, PrivateAttr 
from abc import ABC, abstractmethod
from qdrant_client import QdrantClient, models


class VectorStore(BaseModel, ABC):
    """Vector database used to store embeddings."""
    
    url : str = Field(description="Used to communicate with the specific vector db.")
    
    @abstractmethod
    def create_collection(self, collection_name: str, vec_size: int, metric: any):
        """Creates a collection in vector store.

        Args:
            collection_name (str): the name of the collection
            vec_size (int): size of vectors (based on embedding model)
            distance (models.Distance): distance metric used to compare vectors.
        """
        pass
    
    @abstractmethod
    def get_collection(self, collection_name: str):
        """Gets an existing colletion handle.

        Args:
            collection_name (str): the name of the collection.
            
        Returns:
        Returns the collection handle or none if collection doesn't exist.
        """
        pass
    
    @abstractmethod
    def query(self):
        pass
    
    @abstractmethod
    def upsert(self):
        pass


class QdrantVectorStore(VectorStore):
    """Qdrant vector store client."""
    
    _client : QdrantClient = PrivateAttr()
    
    def model_post_init(self, context):
        self._client = QdrantClient(url=self.url)

        return super().model_post_init(context)
    
    def create_collection(self, collection_name: str, vec_size: int, metric: models.Distance):
        if not self._client.collection_exists(collection_name=collection_name):
            return self._client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(size=vec_size, distance=metric)
            )
        
        return None
    
    def get_collection(self, collection_name: str):
        pass
    
    def query(self):
        pass
    
    def upsert(self):
        pass
    
    
if __name__ == "__main__":
    qvs = QdrantVectorStore(url="localhost:6333")
    qvs.create_collection("test_collection", 100, models.Distance.COSINE)
    
    