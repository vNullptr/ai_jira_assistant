from pydantic import BaseModel, Field
from uuid import UUID
from typing import Optional
import datetime

from schema.enums import *


class Job(BaseModel):
    uuid : Optional[UUID] = Field(description="Assigned job UUID.")
    issue_key : str = Field(description="Jira issue key.")
    comment_id : int = Field(description="ID of the jira issue comment.")
    author : str = Field(description="Author of the comment.")
    status : JobStatus = Field(description="Status of the job (failed, pending, processing, done)")
    claimed_at : Optional[datetime.datetime] = Field(description="The date and time the job was claimed at.")
    finished_at : Optional[datetime.datetime] = Field(description="The date and time the job was finished at.")
    created_at : Optional[datetime.datetime] = Field(description="The date and time the job was created.")