from fastapi import APIRouter, Response, Request

router = APIRouter(
    prefix="/webhooks"
)

@router.post("")
async def trigger(request : Request):
    body = await request.json()
    
    return Response(status_code=200)