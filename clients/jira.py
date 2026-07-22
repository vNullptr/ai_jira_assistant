from pydantic import BaseModel, PrivateAttr, Field, computed_field, field_validator
from abc import ABC, abstractmethod
import httpx, asyncio, json

class JiraClient(BaseModel, ABC):
    """Jira Client used to communicate with a project."""
    
    @abstractmethod
    def get_issue_comments(id: int) -> list:
        """Fetchs comments from an issue by id.

        Args:
            id (int): id of the jira issue.
            
        Returns:
        Returns a list of json objects containing all the comments.
        """
        pass

class JiraAPIClient(JiraClient):
    """Jira client communicating through the API."""
    domain : str = Field(description="User JIRA domain.")
    auth_mail : str = Field(description="Email address used to auth to Jira API.")
    api_token : str = Field(description="API Token used to auth to Jira API.")
    _client : httpx.AsyncClient = PrivateAttr()
    
    def model_post_init(self, context):
        self._client = httpx.AsyncClient(
            base_url=self.api_url,
            timeout=30,
            auth=httpx.BasicAuth(self.auth_mail, self.api_token),
            headers={
                'Accept': 'application/json'
            }
        )
        return super().model_post_init(context)
    
    @field_validator("domain")
    @classmethod
    def strip_scheme(cls, v: str) -> str:
        return v.removeprefix("https://").removeprefix("http://").rstrip("/")
    
    @computed_field
    @property
    def api_url(self) -> str:
        return f"https://{self.domain}/rest/api/3"
    
    async def get_issue_comments(self, id: int) -> list:
        response = await self._client.get(f"issue/{id}/comment")
        # TODO: Handling wrong status code with tenacity retry
        if response.status_code == 200:
            return json.loads(response.content)
