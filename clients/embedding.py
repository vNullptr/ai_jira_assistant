from pydantic import BaseModel, Field, PrivateAttr
from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings.embeddings import Embeddings

from langfuse import observe

class EmbeddingClient(BaseModel, ABC):
    
    model_name: str = Field(description="Embedding model name.", frozen=True)
    _dimension: int = PrivateAttr(default=None)
    _client : Embeddings = PrivateAttr()
    
    @abstractmethod
    def embed_query(self, input: str)->list[float]:
        """Tokenizes and embeds a str input.

        Args:
            input (str): string input to embed.

        Returns:
            output (list[float]): Returns a vector.
        """
        pass
    
    @abstractmethod
    def embed_documents(self, input: list[str])->list[list[float]]:
        """Tokenizes the page_content and embeds it.

        Args:
            input (Document): Langchain document instance.

        Returns:
            output (dict["vector", "metadata"]): Returns a dict with the vector and the metadata.d
        """
        
    def get_dimension(self) -> int:
        """Embeds a small string to retrieve the embedding model dimension.

        Returns:
            output (int): Dimension of the embedding model. 
        """
        pass
    
    
class HFEmbeddingClient(EmbeddingClient):
    
    def model_post_init(self, context):
        self._client = HuggingFaceEmbeddings(
            model_name=self.model_name,
        )
        
        return super().model_post_init(context)
    
    @observe(name="HFEmbeddingClient query", as_type="embedding")
    def embed_query(self, input: str)->list[float]:
        result = self._client.embed_query(input)
        
        return result
        
    @observe(name="HFEmbeddingClient documents", as_type="embedding")
    def embed_documents(self, input: list[str])-> list[list[float]]:
        result = self._client.embed_documents(input)
        
        return result
            
    def get_dimension(self) -> int:
        result = self.embed_query("Hello World!")
        
        if not self._dimension:
            self._dimension = len(result)
        
        return self._dimension        