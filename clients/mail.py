from pydantic import BaseModel, Field
from abc import ABC, abstractmethod

class MailClient(BaseModel, ABC):
    domain : str = Field(description="Domain of mail")
    addr : str = Field(description="Mail address to poll from.")
    password : str = Field(description="Mail address password.")


class IMAPMailClient(MailClient):
    pass 

class FakeMailClient(MailClient):
    pass