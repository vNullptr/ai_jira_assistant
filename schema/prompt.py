from pydantic import BaseModel, Field

class PromptSchema(BaseModel):
    """Prompt Schema"""
    
    prompt : str | None = Field()
    role : str = Field(default="human")

    @property
    def structured_prompt(self) -> tuple[str, str]:
        """Structures prompt for langchain invoke().

        Raises:
            RuntimeError: Raises runtime error if prompt field isn't set.

        Returns:
            Returns valid format prompt based on langchain conventions. 
        """
        if self.prompt is None:
            raise RuntimeError("Missing prompt in PromptSchema.")
        return (self.role,self.prompt)