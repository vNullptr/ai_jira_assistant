from pydantic import BaseModel, PrivateAttr, Field, computed_field, field_validator
from abc import ABC, abstractmethod
import httpx, json

class JiraClient(BaseModel, ABC):
    """Jira Client used to communicate with a project."""
    
    @abstractmethod
    async def get_issue(self, issue_key: str) -> list:
        """Fetchs the issue thread by id.

        Args:
            issue_key (int): jira issue key.
            
        Returns:
        issue_thread (dict): dict containing all the thread.
        """
        pass
    
    @abstractmethod
    async def comment_issue(self, issue_key: str, content: str):
        """Comments on a specific issue.

        Args:
            issue_key (str): jira issue key.
            content (str): content of the comment.

        Returns:
            response (dict): HTTP reponse, None if wrong status code.
        """
        pass
    
    @abstractmethod
    async def update_comment(self, issue_key: str, comment_id: str):
        """Updates/Edits specific comment.
        
        Args:
            issue_key (str): jira issue key.
            comment_id (str): id of comment to update.
            content (str): content of the comment.

        Returns:
            response (dict): HTTP reponse, None if wrong status code.
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
                'Accept': 'application/json',
                "Content-Type": "application/json"
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
    
    async def get_issue(self, issue_key: str) -> list:
        response = await self._client.get(f"issue/{issue_key}")
        # TODO: Handling wrong status code with tenacity retry
        if response.status_code == 200:
            return json.loads(response.content)
        
    async def comment_issue(self, issue_key: str, content: str):
        payload = json.dumps({
        "body": {
            "content": [
            {
                "content": [
                {
                    "text": content,
                    "type": "text"
                }
                ],
                "type": "paragraph"
            }
            ],
            "type": "doc",
            "version": 1
        },
        "properties": [
                {
                    "key": "sd.public.comment",
                    "value": {
                        "internal": True
                    }
                }
            ]
        })
        
        response = await self._client.post(f"issue/{issue_key}/comment",data=payload)
        
        if response.status_code == 201:
            return json.loads(response.content)
        
    
    async def update_comment(self, issue_key: str, comment_id: str, content: str):
        payload = json.dumps({
            "body": {
                "content": [
                {
                    "content": [
                    {
                        "text": content,
                        "type": "text"
                    }
                    ],
                    "type": "paragraph"
                }
                ],
                "type": "doc",
                "version": 1
            },
            "properties": [
                {
                    "key": "sd.public.comment",
                    "value": {
                        "internal": True
                    }
                }
            ]
        })
        
        response = await self._client.put(f"issue/{issue_key}/comment/{comment_id}",data=payload)
        
        if response.status_code == 200:
            return json.loads(response)
        
