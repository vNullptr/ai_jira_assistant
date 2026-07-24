from fastapi import APIRouter, Response, Request

from services.jobqueue import *
from config import Settings
import re


settings = Settings()
runner = asyncio.Runner(loop_factory=asyncio.WindowsSelectorEventLoopPolicy().new_event_loop)
pgdc = PostgresDatabaseClient(user=settings.POSTGRES_USER, password=settings.POSTGRES_PASSWORD, dbname=settings.POSTGRES_DBNAME)
jq = JobQueue(database_client=pgdc)

router = APIRouter(
    prefix="/webhooks"
)

@router.post("")
async def trigger(request : Request):
    body = await request.json()

    if not body["comment"]["jsdPublic"]:
        await jq.init()
        await jq.queue(
            issue_key=body["issue"]["key"],
            comment_id=body["comment"]["id"],
            author=body["comment"]["author"]["accountId"]
            )
    
    return Response(status_code=200)