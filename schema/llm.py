from pydantic import BaseModel, Field
from ollama import chat

from schema.prompt import PromptSchema


class LLMClient(BaseModel):
    model_name : str = Field()

    
    
class MistralClient(LLMClient):
        
    def prompt(self, prompt : PromptSchema) -> any:
            print(self.model_name)

            result = chat(
                model=self.model_name,
                messages=[prompt],
                )
        
        
if __name__ == "__main__":
    mc = MistralClient(model_name="test")
    promptModel = PromptSchema(role="test", prompt="test")
    mc.prompt(promptModel)
    
    