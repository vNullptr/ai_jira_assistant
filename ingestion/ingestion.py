from pydantic import BaseModel, Field, PrivateAttr
from ingestion.parser import Parser
from clients.embedding import EmbeddingClient
from clients.vectordb import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

import uuid, transformers

class IngestionPipeline(BaseModel):
    
    parser : Parser = Field(description="Parser used for the corpus during the ingestion.")
    embedding_client : EmbeddingClient = Field(description="Embedding client used to embed document chunks.")
    vectorstore : VectorStore = Field(description="Vector databse client used to store embedding.")
    collection_name : str = Field(description="Name of collection.")
    batch_size : int = Field(description="Size of batch.")
    clear : bool = Field(description="Whether or not to clear the collection if it exists.", default=False)
    _documents = PrivateAttr(default=[])
    
    def init(self):
        #Loads corpus
        pass
    
    def run(self): 
        
        result : list[dict] = []
        if not self._documents:
            raise ValueError("Missing documents.")
            
        # Parsing
        result.extend(self.parser.parse(self._documents))
           
        if not self.vectorstore.collection_exists(self.collection_name):
            self.vectorstore.create_collection(
                collection_name=self.collection_name, 
                vec_size=self.embedding_client.get_dimension(), 
                metric="Cosine"
            )
        elif self.clear:
            self.vectorstore.clear(collection_name=self.collection_name)
            
        # Chunking 
        chunks = []  
        tokenizer = transformers.AutoTokenizer.from_pretrained("intfloat/multilingual-e5-large")
        splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            separators=[".", "\n\n", "\n"],
            chunk_size=500,
            chunk_overlap=100,
            tokenizer=tokenizer
        )
        for page in result:
            slices = splitter.split_text(page.get("content"))
            chunks.extend([{"content":s, "metadata":page.get("metadata")} for s in slices])
        
        # Batching 
        batchs = [chunks[x:x+self.batch_size] for x in range(0, len(chunks), self.batch_size)]
        for batch in batchs:
            text = [chunk.get("content") for chunk in batch]
            metadatas = [chunk.get("metadata") for chunk in batch]
            
            # Embedding
            embeddings = self.embedding_client.embed_documents(text)
            
            # Saving
            uuids = [uuid.uuid4() for _ in range(len(embeddings))]
            self.vectorstore.upsert(self.collection_name, uuids, embeddings, metadatas)     