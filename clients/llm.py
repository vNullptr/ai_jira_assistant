from pydantic import BaseModel, Field
from typing import Optional, ClassVar
from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama
from langchain_core.prompts import BaseChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.messages.ai import AIMessage
from langfuse import observe

from schema.prompt import extraction_prompt
from config import Settings

class LLMClient(BaseModel, ABC):
    model_name : str = Field()
    # TODO : Useless here needs to be moved elsewhere
    settings : ClassVar = Settings() 
    
    @abstractmethod
    def prompt(self, prompt_template : BaseChatPromptTemplate, prompt_content : dict = None) -> AIMessage:
        """Prompts the model with a specific prompt template and content.

        Args:
            prompt_template (BaseChatPromptTemplate): The langchain prompt template
            prompt_content (Optional, dict): Dictionary to inject inside the prompt template

        Returns:
            AIMessage : LLM answer.
        """
        pass

    
class MistralClient(LLMClient):
    """Client for ollama Mistral model"""
    
    model_name : str = "mistral"
    temperature : float = Field(ge=0, le=2) # not on the abs because range differs from model to another
    client : Optional[BaseChatModel] = None
        
    def model_post_init(self, context: any) -> None: 
        self.client = ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            validate_model_on_init=True,
        )

    @observe(name="Mistral Prompt")
    def prompt(self, prompt_template : BaseChatPromptTemplate, prompt_content : dict = None) -> AIMessage:
        
        chain = (prompt_template
            | self.client)
        result = chain.invoke(prompt_content)
        
        return result 
        