from fastapi import APIRouter, Response
import asyncio

from schema.requests import Request
from services.jobqueue import *
from config import Settings


settings = Settings()
runner = asyncio.Runner()
pgdc = PostgresDatabaseClient(host=settings.POSTGRES_HOST,  user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD, dbname=settings.POSTGRES_DBNAME)
jq = JobQueue(database_client=pgdc)

router = APIRouter(
    prefix="/webhooks"
)

@router.post("")
async def trigger(request : Request):
    
    if not request.comment.jsdPublic and request.comment.body.strip("") == "/assist":
        await jq.init()
        await jq.queue(
            issue_key=request.issue.key,
            comment_id=request.comment.id,
            author=request.comment.author.accountId
            )
    
    return Response(status_code=200)