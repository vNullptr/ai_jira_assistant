from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional

from services.jobqueue import JobQueue
from clients.database import DatabaseClient
from clients.jira import JiraClient, format_issue_thread
from clients.llm import LLMClient
from schema.enums import *
from schema.job import Job
from langfuse import observe

class Worker(BaseModel):
    database_client : DatabaseClient = Field(description="Database client used to establish connection and manage queue.")
    jira_client : JiraClient = Field(description="Jira client used to communicate with JSM.")
    llm_client : LLMClient = Field(description="LLM client used for inference.")
    status : Optional[WorkerStatus] = Field(description="Defines the status of the worker.", default=WorkerStatus.AVAILABLE)
    current_job : Optional[Job] = Field(description="ID of the issue being currently processed.", default=None)
    _jobqueue : JobQueue = PrivateAttr()
    
    def model_post_init(self, context):
        self._jobqueue = JobQueue(database_client=self.database_client)
        
        return super().model_post_init(context)
    
    async def start(self):
        """Initializes the worker.
        """
        # TODO: initializing sanity check.
        await self._jobqueue.init()
    
    def pause(self):
        pass
    
    def end(self):
        pass
    
    async def next(self):
        """Claims next pending job.
        """
        if (not self.current_job) and self.status == WorkerStatus.AVAILABLE:
            self.current_job = await self._jobqueue.head(JobStatus.PENDING)
            #await self._jobqueue.update_status(self.current_job.uuid, JobStatus.PROCESSING)
    
    @observe(name="Processing Chain", as_type="chain")        
    async def process(self):
        """Processes current claimed job.
        """
        if self.status == WorkerStatus.AVAILABLE and self.current_job:
            self.status = WorkerStatus.PROCESSING
                
            issue_thread = await self.jira_client.get_issue(self.current_job.issue_key)
        
            response = await self.jira_client.comment_issue(self.current_job.issue_key, "Processing...")
            
            # format >
            formatted_thread = format_issue_thread(issue_thread)
            # template > chain > answer
            answer = self.llm_client.prompt("issue-thread-prompt", {"thread":formatted_thread})
            
            await self.jira_client.update_comment(self.current_job.issue_key, response["id"], answer.content)
            
            self.status = WorkerStatus.AVAILABLE
            
            
# testing
if __name__ == "__main__":
    from clients.jira import JiraAPIClient
    from clients.database import PostgresDatabaseClient
    from clients.llm import MistralClient
    from langfuse import get_client
    from config import Settings
    import asyncio
    
    settings = Settings()
    lf_client = get_client()
    
    jac = JiraAPIClient(domain=settings.JIRA_DOMAIN, auth_mail=settings.JIRA_AUTH_MAIL, api_token=settings.JIRA_API_TOKEN)
    pdc = PostgresDatabaseClient(user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD, dbname=settings.POSTGRES_DBNAME)
    mc = MistralClient(langfuse_client=lf_client, temperature=0)
    
    worker = Worker(database_client=pdc, jira_client=jac, llm_client=mc)
    
    runner = asyncio.Runner(loop_factory=asyncio.WindowsSelectorEventLoopPolicy().new_event_loop)
    runner.run(worker.start())
    runner.run(worker.next())
    runner.run(worker.process())
            
            
              