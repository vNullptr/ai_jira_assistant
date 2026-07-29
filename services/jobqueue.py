from pydantic import BaseModel, Field
from clients.database import  DatabaseClient, PostgresDatabaseClient # for webhook import
import uuid

from schema.job import Job
from schema.enums import *

class JobQueue(BaseModel):
    database_client : DatabaseClient = Field(description="Database client used to establish connection and query.")
    
    async def init(self):
        """Initializes the queue by creating types and tables if missing.
        """
        
        await self.database_client.connect()
        
        await self.database_client.exec("SELECT 1 FROM pg_type WHERE typname='processing_status'")
        type_check = await self.database_client.fetch() 
                
        # PG doesn't support IF NOT EXISTS on TYPE    
        if not type_check:
            await self.database_client.exec("""
                CREATE TYPE PROCESSING_STATUS AS ENUM ('failed','pending','processing','done')
            """)

        await self.database_client.exec("""
            CREATE TABLE IF NOT EXISTS queue(
                uuid UUID PRIMARY KEY default gen_random_uuid(), 
                issue_key TEXT NOT NULL,
                comment_id TEXT NOT NULL,
                author TEXT NOT NULL,
                status PROCESSING_STATUS NOT NULL DEFAULT 'pending',
                claimed_at TIMESTAMP DEFAULT NULL,
                finished_at TIMESTAMP DEFAULT NULL,
                created_at TIMESTAMP DEFAULT now()
            )""")
        
        
        await self.database_client.exec("""
            CREATE INDEX IF NOT EXISTS queue_indexes
            ON queue (claimed_at, created_at, status)
            """)
        
    
    async def head(self, status : JobStatus) -> Job:
        """Gets the oldest entry of the specified status.

        Args:
            status (JobStatus): Status to filter with.

        Returns:
            Job (Job): Constructed Job object if occurence found other wise returns None. 
        """
        await self.database_client.exec("SELECT * FROM queue WHERE status = %s ORDER BY created_at ASC LIMIT 1", (status.value,))
        result = await self.database_client.fetch()
        
        if result: 
            return Job(**result[0])
        
        return None 
    
    async def claim_head(self, status : JobStatus) -> Job:
        """Claims the head by locking thw row until status is updating to avoid concurrent processing.
        
        Args:
            status (JobStatus): Status to filter with.

        Returns:
            Job (Job): Constructed Job object if occurence found other wise returns None. 
        """
        await self.database_client.exec("""
                UPDATE queue SET status=%s, claimed_at=now() 
                WHERE uuid=(SELECT uuid FROM queue WHERE status=%s ORDER BY created_at ASC LIMIT 1 FOR UPDATE SKIP LOCKED) 
                RETURNING *;""", (JobStatus.PROCESSING.value, status.value))
        result = await self.database_client.fetch()
        
        if result: 
            return Job(**result[0])
        
        return None
    
    async def get_job_by_uuid(self, uuid : uuid.UUID) -> Job:
        """Gets job by uuid.

        Args:
            uuid (uuid.UUID): UUID used for the search.

        Returns:
            Job: returns a job if found.
        """
        await self.database_client.exec("SELECT * FROM queue WHERE uuid = %s", (uuid,))
        result = await self.database_client.fetch()
        
        if result:
            return Job(**result[0])
        
        return None
    
    async def get_jobs_by_status(self, status : JobStatus) -> list[Job]:
        """Get a jobs with a specific status

        Args:
            status (JobStatus): Status to filter with.

        Returns:
            list[Job]: list of constructed jobs. return empty list if none found
        """
        await self.database_client.exec("SELECT * FROM queue WHERE status = %s", (status.value,))
        result = await self.database_client.fetch()
        
        return [Job(**occ) for occ in result]
    
    
    async def update_status(self, uuid : uuid.UUID, status : JobStatus):
        """Updates the status of a specific job.

        Args:
            uuid (uuid.UUID): UUID of the job
            status (JobStatus): New job status. 

        """
        timestamp = ""
        match status:
            case JobStatus.PROCESSING:
                timestamp = ", claimed_at = now()"
            case JobStatus.PENDING:
                # TODO: might add a attempts column and order using it.
                # this is for retry logic.
                timestamp = ", created_at = now() , claimed_at = NULL"
            case JobStatus.DONE:
                timestamp = ", finished_at = now()"
            
        await self.database_client.exec(f"UPDATE queue SET status = %s {timestamp} WHERE uuid = %s", (status.value, str(uuid)))
    
    async def all(self) -> list[Job]:
        """Gets all the queue.

        Returns:
            list[Job]: List of constructed Jobs.
        """
        await self.database_client.exec("SELECT * FROM queue")
        result = await self.database_client.fetch()
        
        return [Job(**occ) for occ in result]
    
    async def queue(self, issue_key: str, comment_id: str, author: str):
        """Insert a new job to the queue.

        Args:
            issue_id (int): Job containing issue id and status.
        """
        await self.database_client.exec("INSERT INTO queue(issue_key, comment_id, author) VALUES (%s, %s, %s)", (issue_key, comment_id, author))
        
    
        
    async def sweep(self):
        #TODO: refactor when concurrency implemented
        result = await self.get_jobs_by_status(JobStatus.PROCESSING)
        
        for job in result:
            await self.update_status(job.uuid, JobStatus.PENDING)
        