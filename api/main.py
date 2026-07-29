from fastapi import FastAPI
from api.routes import webhooks

app = FastAPI()

# TODO : Recursive auto router include
app.include_router(webhooks.router)

@app.get("/")
def notify():
    return {"status":"online"}
