from pydantic import BaseModel, Field, PrivateAttr
from abc import ABC, abstractmethod
from typing import Any
import psycopg
from psycopg.rows import dict_row
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class DatabaseClient(BaseModel, ABC):
    host : str = Field(description="Database server hostname.", default="localhost")
    port : int = Field(description="Database server post.")
    user : str = Field(description="Database server user.")
    password : str = Field(description="Database server user password.")
    dbname : str = Field(description="Database name.")
    
    _client : Any = PrivateAttr()

    @abstractmethod
    async def connect(self):
        """Connects to the database.
        """
        pass

    @abstractmethod
    async def exec(self, sql: str, params: tuple = None, commit: bool=True):
        """Executes the passed sql with the params.

        Args:
            sql (str): sql query.
            params (tuple): params.
            commit (bool): if it should commit the transaction or not. Default True.
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
    async def manual_commit(self):
        """Manually commits a transaction.
        """
        pass
    
    @abstractmethod
    async def close(self):
        """Closes the connection to Database"""
        pass


class PostgresDatabaseClient(DatabaseClient):
    _client : psycopg.Connection = PrivateAttr()
    _cursor : psycopg.Cursor = PrivateAttr()
    port : int = Field(description="Database server post.", default=5432)
    
    @retry(stop=stop_after_attempt(4), wait=wait_exponential(1, 30), reraise=True)
    async def connect(self):
        self._client = await psycopg.AsyncConnection.connect(f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}")
        self._cursor = self._client.cursor(row_factory=dict_row)
    
    async def exec(self, sql: str, params: tuple = None, commit=True):
        await self._cursor.execute(sql, params)
        if commit:
            await self._client.commit()
        
        return self
    
    async def fetch(self) -> list:
        result = await self._cursor.fetchall()
        
        return result 
    
    async def manual_commit(self):
        await self._client.commit()
        
        
    async def close(self):
        await self._client.close()