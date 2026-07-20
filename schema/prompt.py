from pydantic import BaseModel, Field

class PromptSchema(BaseModel):
    prompt : str | None = Field()
    role : str = Field(default="user")

    @property
    def structured_prompt(self) -> dict[str, str]:
        if self.prompt is None:
            raise RuntimeError("Missing prompt in PromptSchema.")
        return {"role":self.role, "message":self.prompt} 