from fastapi import FastAPI
from pydantic import BaseModel
from mangum import Mangum
from datetime import datetime

import os

stage = os.environ.get('STAGE', None)
openapi_prefix = f"/{stage}" if stage else "/"


app = FastAPI(title="serverless-app", openapi_prefix=openapi_prefix)


class Item(BaseModel):
    dataProduto: str
    macroProcesso: str
    nome: str
    periodicidade: datetime
    periodicidadFinal: datetime
    processo: str
    url: str


@app.post("/webhook")
async def webhook(item: Item):
    print(item)
    return item


handler = Mangum(app)
