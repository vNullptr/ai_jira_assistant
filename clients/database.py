from pydantic import BaseModel, Field, PrivateAttr
from abc import ABC, abstractmethod
import psycopg 
from uuid import UUID, uuid4

from schema.enums.jobstatus import JobStatus
from schema.job import Job
from config import Settings

settings = Settings()

class DatabaseClient(BaseModel, ABC):
    host : str = Field(description="Database server hostname.")
    port : int = Field(description="Database server post.")
    user : str = Field(description="Database user.")
    password : str = Field(description="Database user password.")
    
    _client : any = PrivateAttr()

    @abstractmethod
    def exec(self, sql: str, params: tuple = None):
        """Executes the passed sql with the params.

        Args:
            sql (str): sql query.
            params (tuple): params
        """
        pass

    @abstractmethod
    def fetch(self) -> list:
        """Fetchs previous query result.
        Returns:
            row list: list of resulting rows.
        """
        pass
    
    @abstractmethod
    def close(self):
        """Closes the connection to Database"""
        pass


class PostgresDatabaseClient(DatabaseClient):
    _client : psycopg.Connection = PrivateAttr()
    _cursor : psycopg.Cursor = PrivateAttr()
    port : int = 5432
    
    def model_post_init(self, context):
        self._client = psycopg.connect(f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/jira_assistant_queue")
        self._cursor = self._client.cursor()
        
        return super().model_post_init(context)
    
    def exec(self, sql: str, params: tuple = None):
        self._cursor.execute(sql, params)
        self._client.commit()
        
        return self
    
    def fetch(self) -> list:
        return self._cursor.fetchall() 
        
        
    def close(self):
        self._client.close()