from pydantic import BaseModel, Field, PrivateAttr
from langchain_core.language_models import BaseChatModel
from ragas import EvaluationDataset, evaluate
from ragas.metrics.collections import Faithfulness, SummaryScore
from ragas.llms import LangchainLLMWrapper
from langchain_ollama import ChatOllama

class RagasEval(BaseModel):
    
    model_name : str = Field(default="mistral", frozen=True)
    temperature : float = Field(ge=0, le=2, default=0)
    base_url : str = Field(description="base url ollama is hosted on.", default="localhost:11434")
    _client : BaseChatModel = PrivateAttr()

    def model_post_init(self, context):
        
        self._client = ChatOllama(
            model=self.model_name,
            temperature=self.temperature,
            base_url=self.formatted_url
        )
        
        return super().model_post_init(context)

    @staticmethod
    def load_dataset():
        """Loads a dataset.
        """
        pass

    async def eval(self, prompt : str, context : str, response : str) -> dict:
        """Faithfulness evaluation using ragas.
        """
        dataset = EvaluationDataset.from_dict({
            "user_input": prompt, 
            "retrieved_contexts": [context],         
            "reference_contexts": [context],         
            "response": response,                           
        })
        
        wrapped_llm = LangchainLLMWrapper(self._client)
        faithfulness = Faithfulness(llm=wrapped_llm)
        summary = SummaryScore(llm=wrapped_llm)
        metrics = [faithfulness, summary]
        
        
        results = await evaluate(
            dataset=dataset,
            metrics=metrics
        ) 
        
        return results