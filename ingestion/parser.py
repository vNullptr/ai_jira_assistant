from pydantic import BaseModel
from abc import ABC, abstractmethod


class Parser(BaseModel, ABC):
    # Stub/Placeholder
    @abstractmethod
    def parse():
        pass
    