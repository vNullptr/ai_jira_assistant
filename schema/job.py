from pydantic import BaseModel, Field
from uuid import UUID
from schema.enums.jobstatus import JobStatus

class Job(BaseModel):
    uuid : UUID = Field(description="Assigned job UUID.")
    issue_id : int = Field(description="Jira issue ID.")
    status : JobStatus = Field(description="Status of the job (failed, pending, processing, done)")
    
    @property
    def formatted(self):
        return (self.uuid, self.issue_id, self.status.value)