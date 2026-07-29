from pydantic import BaseModel, Field, PrivateAttr
from ingestion.parser import Parser
from clients.embedding import EmbeddingClient
from clients.vectordb import VectorStore

from langchain_core.documents import Document
import uuid

class IngestionPipeline(BaseModel):
    
    parser : Parser = Field(description="Parser used for the corpus during the ingestion.")
    embedding_client : EmbeddingClient = Field(description="Embedding client used to embed document chunks.")
    vectorstore : VectorStore = Field(description="Vector databse client used to store embedding.")
    collection_name : str = Field(description="Name of collection.")
    batch_size : int = Field(description="Size of batch.")
    _documents = PrivateAttr(default=[])
    
    def init(self):
        #Loads corpus
        pass
    
    def run(self):
        #Parse > Batch > NumBatch x [Embed > Store] 
        collection_dimension = self.embedding_client.get_dimension()
        
        result : list[dict] = []
        if self._documents:
            result.extend(self.parser.parse(self._documents))
            # should raise of documents missing
           
        # Chunking here
        chunks = []
        
         
        batchs = [chunks[x:x+self.batch_size] for x in range(0, len(chunks), self.batch_size)]
        for batch in batchs:
            text = [chunk.get("content") for chunk in batch]
            metadatas = [chunk.get("metadata") for chunk in batch]
            
            embeddings = self.embedding_client.embed_documents(text)
            
            uuids = [uuid.uuid4() for _ in range(len(embeddings))]
            self.vectorstore.upsert(self.collection_name, uuids, embeddings, metadatas)                    