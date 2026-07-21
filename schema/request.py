from pydantic import BaseModel, Field
from typing import List
from langchain.tools import tool 

class ExtractedMailData(BaseModel):
    client : str | None = Field(description="Name of the client reporting.")
    product : List[str] = Field(description="List of affected products.")
    rtype : str = Field(description="Request type (Evolution/Incident/...)")
    priority : int = Field(description="Priority/severity of the report.")
    description : str = Field(description="Short description summarizing the initial report.")
    base_txt : str = Field(description="Base report text.")
    