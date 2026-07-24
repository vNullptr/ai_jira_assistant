from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional, ClassVar, List, Any
from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.messages.ai import AIMessage
from langfuse import observe, get_client, Langfuse

from config import Settings

class LLMClient(BaseModel, ABC):
    model_name : str = Field()
    # TODO : Useless here needs to be moved elsewhere
    settings : ClassVar = Settings() 
    tools : List[Any] = []
    
    @abstractmethod
    def prompt(self, prompt_template_name : str, prompt_content : dict = None) -> AIMessage:
        """Prompts the model with a specific prompt template and content.

        Args:
            prompt_template_name (str): Langfuse prompt template name.
            prompt_content (Optional, dict): Dictionary to inject inside the prompt template

        Returns:
            AIMessage : LLM answer.
        """
        pass

    
class MistralClient(LLMClient):
    """Client for ollama Mistral model"""
    
    model_name : str = Field(default="mistral", frozen=True)
    temperature : float = Field(ge=0, le=2) # not on the abs because range differs from model to another
    _client : BaseChatModel = PrivateAttr()
    langfuse_client : Optional[Any] = None
        
    def model_post_init(self, context: Any) -> None:
        
        self._client = ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            validate_model_on_init=True,
        )
        if not self.langfuse_client:
            self.langfuse_client = get_client()
        
        if len(self.tools):
            self._client.bind_tools(self.tools)

    @observe(name="Mistral Prompt", as_type="generation")
    def prompt(self, prompt_template_name : str, prompt_content : dict = None) -> AIMessage:
        
        prompt_template = self.langfuse_client.get_prompt(prompt_template_name, label="production")
        
        self.langfuse_client.update_current_generation(
            prompt=prompt_template
        )
        
        chain = (ChatPromptTemplate(prompt_template.get_langchain_prompt())
            | self._client)
        result = chain.invoke(prompt_content)
        
        
        return result 