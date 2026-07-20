from pydantic import BaseModel, Field
from typing import List

class ExtractedMailData(BaseModel):
    client : str | None
    product : List[str]
    rtype : str
    priority : int
    description : str
    base_txt : str 