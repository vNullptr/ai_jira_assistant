from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama
from langchain_core.prompts import BaseChatPromptTemplate

from schema.prompt import basePrompt


class LLMClient(BaseModel, ABC):
    model_name : str = Field()
    
    @abstractmethod
    def prompt(self, prompt : BaseChatPromptTemplate, temperature : int = 0):
        """Prompts the llm model.

        Args:
            prompt (PromptSchema): Prompt to be passed to the llm.
            temperature (int, optional): Temperature of model. 
        """
        pass

    
    
class MistralClient(LLMClient):
    """Client for ollama Mistral model"""
        
    def prompt(self, prompt : BaseChatPromptTemplate, temperature : int = 0) -> any:
        pass
        
        
if __name__ == "__main__":
    mc = MistralClient(model_name="test")
    promptModel = PromptSchema(prompt="test")
    mc.prompt(promptModel)
    
    