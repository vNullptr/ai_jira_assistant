from pydantic import BaseModel, Field

class Author(BaseModel):
    displayName : str = Field(description="Display name of the author of the comment.")
    accountId : str = Field(description="Unique id of the comment author.")

class Comment(BaseModel):
    id : str = Field(description="ID of the Comment in the Issue.")
    author : Author
    body : str = Field(description="Content of the comment.")
    jsdPublic : bool = Field(description="Whether the comment is public or internal.")
 
class Issue(BaseModel):
    key : str = Field(description="Jira Issue key based on project name.")
    
class Request(BaseModel):
    comment : Comment 
    issue : Issue