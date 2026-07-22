from fastapi import FastAPI
from api.routes import webhooks

client = FastAPI()

# TODO : Recursive auto router include
client.include_router(webhooks.router)

@client.get("/")
def notify():
    return {"status":"online"}
