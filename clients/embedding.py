from pydantic import BaseModel, Field, PrivateAttr
from abc import ABC, abstractmethod

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.embeddings.embeddings import Embeddings

from langfuse import observe

class EmbeddingClient(BaseModel, ABC):
    
    model_name: str = Field(description="Embedding model name.")
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
    def embed_document(self, input: Document)->dict:
        """Tokenizes the page_content and embeds it.

        Args:
            input (Document): Langchain document instance.

        Returns:
            output (dict["vector", "metadata"]): Returns a dict with the vector and the metadata.d
        """
    
    
class HFEmbeddingClient(EmbeddingClient):
    
    def model_post_init(self, context):
        self._client = HuggingFaceEmbeddings(
            model_name=self.model_name
        )
        
        return super().model_post_init(context)
    
    @observe(name="HFEmbeddingClient query", as_type="embedding")
    def embed_query(self, input: str)->list[float]:
        result = self._client.embed_query(input)
        
        return result
        
    @observe(name="HFEmbeddingClient documents", as_type="embedding")
    def embed_document(self, input: Document)-> dict:
        result = self._client.embed_query(input.page_content)
        
        return {"content": result, "metadata": input.metadata}
            
            
        