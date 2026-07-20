from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama

from schema.prompt import PromptSchema


class LLMClient(BaseModel):
    model_name : str = Field()

    
    
class MistralClient(LLMClient):
        
    def prompt(self, prompt : PromptSchema) -> any:
        
        
        
if __name__ == "__main__":
    mc = MistralClient(model_name="test")
    promptModel = PromptSchema(role="test", prompt="test")
    mc.prompt(promptModel)
    
    