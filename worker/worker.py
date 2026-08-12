from pydantic import BaseModel, Field, PrivateAttr
from typing import Optional
import asyncio
from langfuse import observe

from services.jobqueue import JobQueue
from clients.database import DatabaseClient
from clients.jira import JiraClient, format_issue_thread
from clients.llm import LLMClient
from schema.enums import *
from schema.job import Job
from ..log_config import configure_logging, logger
from schema.exceptions import RetryableException, TerminalException 

class Worker(BaseModel):
    database_client : DatabaseClient = Field(description="Database client used to establish connection and manage queue.")
    jira_client : JiraClient = Field(description="Jira client used to communicate with JSM.")
    llm_client : LLMClient = Field(description="LLM client used for inference.")
    status : Optional[WorkerStatus] = Field(description="Defines the status of the worker.", default=WorkerStatus.AVAILABLE)
    current_job : Optional[Job] = Field(description="ID of the issue being currently processed.", default=None)
    _jobqueue : JobQueue = PrivateAttr()
    
    def model_post_init(self, context):
        self._jobqueue = JobQueue(database_client=self.database_client)
        configure_logging()
        
        return super().model_post_init(context)
    
    async def start(self):
        """Initializes the worker.
        """
        # initializing + sanity check.
        await self._jobqueue.init()
        await self._jobqueue.sweep()
        
        while True:
            await self.next()
            
            if not self.current_job:
                await asyncio.sleep(2)
                continue
            
            try:
                logger.info(f"Job found (id:{self.current_job.uuid})")
                await self.process()
            except TerminalException as e:
                await self._jobqueue.update_status(self.current_job.uuid, JobStatus.FAILED)
                logger.error("Job failed: ", e)
                self._flush()
            except RetryableException as e:
                await self._jobqueue.update_status(self.current_job.uuid, JobStatus.PENDING)
                logger.warning("Job failed placed at the back of queue: ", e)
                self._flush()
                
    
    def pause(self):
        pass
    
    async def end(self):
        await self.database_client.close()
        
    def _flush(self):
        """Flush current state of worker resetting current job and restoring status to available.
        """
        self.current_job = None
        self.status = WorkerStatus.AVAILABLE
    
    async def next(self):
        """Claims next pending job.
        """
        if (not self.current_job) and self.status == WorkerStatus.AVAILABLE:
            self.current_job = await self._jobqueue.claim_head(JobStatus.PENDING)
    
    @observe(name="Processing Chain", as_type="chain")        
    async def process(self):
        """Processes current claimed job.
        """
        if self.status == WorkerStatus.AVAILABLE and self.current_job:
            self.status = WorkerStatus.PROCESSING
                
            issue_thread = await self.jira_client.get_issue(self.current_job.issue_key)
        
            response = await self.jira_client.comment_issue(self.current_job.issue_key, "Processing...")
            
            formatted_thread = format_issue_thread(issue_thread)
            # template > chain > answer
            answer = self.llm_client.prompt("issue-thread-prompt", {"thread":formatted_thread})
                
            upd_response = await self.jira_client.update_comment(self.current_job.issue_key, response["id"], answer.content)
            # returns None if 404 ("Processing..." comment not found)
            if not upd_response:
                response = await self.jira_client.comment_issue(self.current_job.issue_key, answer.content)
            
            await self._jobqueue.update_status(self.current_job.uuid, JobStatus.DONE)
  
            self.current_job = None
            self.status = WorkerStatus.AVAILABLE
            
            
              