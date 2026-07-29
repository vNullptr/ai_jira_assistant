from pydantic import BaseModel, Field, PrivateAttr 
from abc import ABC, abstractmethod
from qdrant_client import QdrantClient, models
from typing import Any


class VectorStore(BaseModel, ABC):
    """Vector database used to store embeddings."""
    
    url : str = Field(description="Used to communicate with the specific vector db.")
    
    @abstractmethod
    def create_collection(self, collection_name: str, vec_size: int, metric: Any):
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
            Collection: Returns the collection handle or none if collection doesn't exist.
        """
        pass
    
    @abstractmethod
    def query(self, collection_name: str, query_vec: list[float], top_k: int = 1, filter : Any = None, params : Any = None) -> Any:
        """Returns the closest k vectors.

        Args:
            collection_name (str): name of collection to query.
            query_vec (list[float]): target search vector.
            filter (Any, optional): filter configuration. Defaults to None.
            params (Any, optional): search parameters. Defaults to None.
        """
        pass
    
    @abstractmethod
    def upsert(self, collection_name: str, ids: list[str], vectors: list[list[float]], metadatas: list[dict]):
        """Upserts given list of vectors.

        Args:
            collection_name (str): name of the vector store collection.
            ids (list[str]): list of ids.
            vectors (list[list[float]]): list of vectors.
            metadatas (list[dict]): list of metadatas.
        """
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
        return None
    
    def query(self, collection_name: str, query_vec: list[float], top_k: int = 1,filter : Any = None, params : Any = None):
        
        hnsw_params = models.SearchParams(hnsw_ef=128, exact=False) if params else params

        result = self._client.query_points(
            collection_name=collection_name,
            query=query_vec,
            query_filter=filter,
            limit=top_k,
            search_params=hnsw_params
        )
        
        return result
    
    def upsert(self, collection_name: str, ids: list[str], vectors: list[list[float]], metadatas: list[dict]):

        # TODO: should check for symmetry before

        points = [
            models.PointStruct(
                id=id, 
                payload=metadata, 
                vector= vec
            ) 
            for id, metadata, vec in zip(ids, vectors, metadatas)]
        
        self._client.upsert(
            collection_name=collection_name,
            points=points
        )
        