from fastapi import APIRouter, Response

from schema.requests import Request
from services.jobqueue import *
from config import Settings

class CommonDependency:
    def __init__(self):
        self.settings = Settings()
        self.pgdc = PostgresDatabaseClient(host=self.settings.POSTGRES_HOST,  user=self.settings.POSTGRES_USER, password=self.settings.POSTGRES_PASSWORD, dbname=self.settings.POSTGRES_DBNAME)
        self.jq = JobQueue(database_client=self.pgdc)
    
dep = CommonDependency()

async def on_startup():
    await dep.jq.init()

router = APIRouter(
    prefix="/webhooks",
    on_startup=[on_startup]
)

@router.post("")
async def trigger(request : Request):
    
    if not request.comment.jsdPublic and request.comment.body.strip() == "/assist":
        await dep.jq.queue(
            issue_key=request.issue.key,
            comment_id=request.comment.id,
            author=request.comment.author.accountId
            )
    
    return Response(status_code=200)