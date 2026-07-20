from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama
from langchain_core.prompts import BaseChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

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
    
    temperature : float = Field(gt=0, lt=2) # not on the abs because range differs from model to another
        
    def model_post_init(self, context: any) -> None: 
        self.client = ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            validate_model_on_init=True,
        )
        
    # still deciding on prototype
    def prompt_ctx(self, prompt_template : BaseChatPromptTemplate, prompt_content : str) -> any:
        pass 
        
         