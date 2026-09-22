from pydantic import BaseModel, Field, PrivateAttr, field_validator, computed_field
from langchain_core.language_models import BaseChatModel
from ragas import EvaluationDataset, evaluate
from ragas.metrics.collections import Faithfulness, SummaryScore
from ragas.llms import llm_factory
from openai import AsyncOpenAI

from log_config import configure_logging, logger

class RagasEval(BaseModel):
    
    model_name : str = Field(default="mistral", frozen=True)
    temperature : float = Field(ge=0, le=2, default=0)
    base_url : str = Field(description="base url ollama is hosted on.", default="localhost:11434")
    _client = PrivateAttr()

    @field_validator("base_url")
    @classmethod
    def strip_scheme(cls, v: str) -> str:
        return v.removeprefix("https://").removeprefix("http://").rstrip("/")
    
    @computed_field
    @property
    def formatted_url(self) -> str:
        return f"http://{self.base_url}/v1/"


    def model_post_init(self, context):
        
        configure_logging()
        
        self._client = AsyncOpenAI(
            base_url=self.formatted_url,
            api_key="ollama"
        )
        
        logger.info("Evaluation LLM loaded.")
        
        return super().model_post_init(context)

    @staticmethod
    def load_dataset():
        """Loads a dataset.
        """
        pass

    async def eval(self, prompt : str, context : str, response : str) -> dict:
        """Faithfulness evaluation using ragas.
        """
        
        logger.info("Starting evaluation.")
        
        llm = llm_factory("mistral", provider="openai", client=self._client)
        faithfulness = Faithfulness(llm=llm)
        summary = SummaryScore(llm=llm)
        
        
        results = {}
        results["faithfulness_score"] = await faithfulness.ascore(
            user_input=prompt, 
            retrieved_contexts=[context], 
            response=response
            )
        results["summary_score"] = await summary.ascore(
            reference_contexts=[context], 
            response=response
        )
        
        
        logger.info("Evaluation done.")
        print(results)
        
        return results