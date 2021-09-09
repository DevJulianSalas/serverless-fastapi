from fastapi import FastAPI
from pydantic import BaseModel


app = FastAPI(title="serverless-app")


class Item(BaseModel):
    temp: float


@app.post("/webhook")
async def webhook(item: Item):
    return item
