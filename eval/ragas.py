from pydantic import BaseModel, Field, PrivateAttr, field_validator, computed_field
from langchain_core.language_models import BaseChatModel
from ragas import EvaluationDataset, experiment
from ragas.metrics.collections import Faithfulness, SummaryScore
from ragas.llms import llm_factory
from openai import AsyncOpenAI

from log_config import configure_logging, logger
from clients.llm import LLMClient

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
        
        return results
    
    

async def _experiment_func(client : LLMClient, prompt_name : str, input : str):
    output = None
    
    #inference and return {response, context}
    
    return output

@experiment()
async def start_parametrized_experiment(self, row, exp_name : str, model_name : str, temperature : float, client : LLMClient, prompt_name : str):
    
    output = await self._experiment_func(client, prompt_name, row["input"])
    
    #eval metrics here
    
    return {
        **row,
        "response": output["response"],
        "experiment_name": f"baseline_{model_name}_{temperature}_{prompt_name}",
        "model_name": model_name, 
        "temperature": temperature
    }