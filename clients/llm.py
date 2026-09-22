from pydantic import BaseModel, Field, PrivateAttr, field_validator, computed_field
from typing import List, Any
from abc import ABC, abstractmethod
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel
from langchain_core.messages.ai import AIMessage
from langfuse import observe, get_client
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx

from log_config import logger
from schema.exceptions import RetryableException

class LLMClient(BaseModel, ABC):
    model_name : str = Field()
    temperature : float = Field(ge=0, le=2)
    tools : List[Any] = []
    
    @abstractmethod
    def get_prompt(self, prompt_template_name : str):
        """Returns the langfuse retrieved prompt

        Args:
            prompt_template_name (str): langfuse prompt name.
            
        Returns:
            langfuse prompt object.
        """
        pass
    
    @abstractmethod
    def infer(self, prompt_template_name : str, prompt_content : dict = None) -> AIMessage:
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
    temperature : float = Field(ge=0, le=2)
    base_url : str = Field(description="base url ollama is hosted on.", default="localhost:11434")
    _client : BaseChatModel = PrivateAttr()
    langfuse_client : Any = None
    
    @field_validator("base_url")
    @classmethod
    def strip_scheme(cls, v: str) -> str:
        return v.removeprefix("https://").removeprefix("http://").rstrip("/")
    
    @computed_field
    @property
    def formatted_url(self) -> str:
        return f"http://{self.base_url}"
        
    def model_post_init(self, context: Any) -> None:
        
        # TODO: request list of working model before requesting.
        self._client = ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.formatted_url
        )
        if not self.langfuse_client:
            logger.warning("missing langfuse client dependency, creating.")
            self.langfuse_client = get_client()


    def get_prompt(self, prompt_template_name : str):
        prompt_template = self.langfuse_client.get_prompt(prompt_template_name, label="production")
            
        return prompt_template
        

    @retry(stop=stop_after_attempt(4), wait=wait_exponential(1, min=10, max=40),  retry=retry_if_exception_type(RetryableException), reraise=True)
    @observe(name="Mistral Prompt", as_type="generation")
    def infer(self, prompt_template_name : str, prompt_content : dict = None) -> AIMessage:
        
        prompt_template = self.get_prompt(prompt_template_name)
        
        self.langfuse_client.update_current_generation(
            prompt=prompt_template
        )
        
        chain = (ChatPromptTemplate(prompt_template.get_langchain_prompt())
            | self._client)
        
        try:
            result = chain.invoke(prompt_content)
        except httpx.ConnectError as e:
            raise RetryableException(f"[LLM] Couldn't reach LLM server ({self.model_name}) : ", e)
        
        return result 