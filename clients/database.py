from pydantic import BaseModel, Field, PrivateAttr
from abc import ABC, abstractmethod
from typing import Any
import psycopg 

from config import Settings

settings = Settings()

class DatabaseClient(BaseModel, ABC):
    host : str = Field(description="Database server hostname.")
    port : int = Field(description="Database server post.")
    user : str = Field(description="Database server user.")
    password : str = Field(description="Database server user password.")
    dbname : str = Field(description="Database name.")
    
    _client : Any = PrivateAttr()

    @abstractmethod
    async def exec(self, sql: str, params: tuple = None):
        """Executes the passed sql with the params.

        Args:
            sql (str): sql query.
            params (tuple): params
        """
        pass

    @abstractmethod
    async def fetch(self) -> list:
        """Fetchs previous query result.
        Returns:
            row list: list of resulting rows.
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Closes the connection to Database"""
        pass


class PostgresDatabaseClient(DatabaseClient):
    _client : psycopg.Connection = PrivateAttr()
    _cursor : psycopg.Cursor = PrivateAttr()
    port : int = 5432
    
    def model_post_init(self, context):
        self._client = psycopg.AsyncConnection()(f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}")
        self._cursor = self._client.cursor()
        
        return super().model_post_init(context)
    
    async def exec(self, sql: str, params: tuple = None):
        await self._cursor.execute(sql, params)
        await self._client.commit()
        
        return self
    
    async def fetch(self) -> list:
        result = await self._cursor.fetchall()
        
        return result 
        
        
    async def close(self):
        await self._client.close()