from fastapi import FastAPI
from pydantic import BaseModel
from mangum import Mangum
import os

stage = os.environ.get('STAGE', None)
openapi_prefix = f"/{stage}" if stage else "/"


app = FastAPI(title="serverless-app", openapi_prefix=openapi_prefix)


class Item(BaseModel):
    temp: float


@app.post("/webhook")
async def webhook(item: Item):
    return item


handler = Mangum(app)
