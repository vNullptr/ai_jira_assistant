from pydantic import BaseModel, Field
from typing import List
from uuid import uuid4


class QueueManager(BaseModel):
    """Manages the extraction queue."""

    current : int | None = Field(default=None)
    
    def add(self, mail : str)-> int:
        """Generates id and stores the request in a table.

        Args:
            mail (str): Mail that needs classification.

        Returns:
            int: id of the stored request.
        """
        id = uuid4()
        
        # save text to db with id attached.
        
        return id
    
    def update(self, id : str):
        pass
        