from fastapi import FastAPI, Request
from pydantic import BaseModel
from mangum import Mangum
from datetime import datetime
from typing import Optional


import os

stage = os.environ.get('STAGE', None)
openapi_prefix = f"/{stage}" if stage else "/"


app = FastAPI(title="serverless-app", openapi_prefix=openapi_prefix)


class Item(BaseModel):
    dataProduto: Optional[str] = None
    macroProcesso: Optional[str] = None
    nome: Optional[str] = None
    periodicidade: Optional[datetime] = None
    periodicidadFinal: Optional[datetime] = None
    processo: Optional[str] = None
    url: Optional[str] = None


@app.post("/webhook")
async def webhook(request: Request, item: Item):
    print(item)
    print(await request.json())
    return item


handler = Mangum(app)
