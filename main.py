import os
from fastapi import FastAPI, Request
from pydantic import BaseModel
from mangum import Mangum
from datetime import datetime
from typing import Optional
import boto3
import json


# Global Variables
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ons_webhook')


stage = os.environ.get('STAGE', None)
openapi_prefix = f"/{stage}" if stage else "/"


app = FastAPI(title="serverless-app", openapi_prefix=openapi_prefix)


def add_item(item):
    response = table.put_item(Item={
        "dataProduto": item['dataProduto'],
        "macroProcesso": item['macroProcesso'],
        "nome": item['nome'],
        "periodicidade": item['periodicidade'],
        "periodicidadeFinal": item['periodicidadeFinal'],
        "processo": item['processo'],
        "url": item['url']
    })
    return response


class Item(BaseModel):
    dataProduto: str
    macroProcesso: str
    nome: str
    periodicidade: str
    periodicidadeFinal: str
    processo: str
    url: str


@app.post("/webhook")
async def webhook(item: Item):
    response = add_item(item)
    print(response)
    return item


handler = Mangum(app)
