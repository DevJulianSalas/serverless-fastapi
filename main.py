import os
import sys
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel
from mangum import Mangum
from datetime import datetime
from typing import Optional
import boto3
import json
import pathlib
import requests


# Global Variables
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
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
    print(item.dict())
    response = add_item(item.dict())
    print(response)
    return item


@app.get("/download_zip")
async def download_zip():
    url = 'https://apps08.ons.org.br/ONS.Sintegre.Proxy/webhook?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVUkwiOiJodHRwczovL3NpbnRlZ3JlLm9ucy5vcmcuYnIvc2l0ZXMvOS8xMy84Mi9Qcm9kdXRvcy8yMzgvTW9kZWxvc19DaHV2YV9WYXphb18yMDIxMTAyNi56aXAiLCJ1c2VybmFtZSI6InJpY2FyZG9AaHVlenRlbGVjb20uY29tLmJyIiwibm9tZVByb2R1dG8iOiJBcnF1aXZvcyBkb3MgbW9kZWxvcyBkZSBwcmV2aXPDo28gZGUgdmF6w7VlcyBkacOhcmlhcyAtIFBEUCIsIklzRmlsZSI6IlRydWUiLCJpc3MiOiJodHRwOi8vbG9jYWwub25zLm9yZy5iciIsImF1ZCI6Imh0dHA6Ly9sb2NhbC5vbnMub3JnLmJyIiwiZXhwIjoxNjM1Mzc5MTAzLCJuYmYiOjE2MzUyOTI0NjN9.xHZ8wQA0ZxVXBvEmJhWf_Dtd8y_wzwm7N8OgB8W6-a4'
    r = requests.get(url, stream=True)
    current_directory = pathlib.Path(__file__).parent.resolve()
    full_path_file = os.path.join(current_directory, 'ons.zip')
    with open(full_path_file, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=128):
            fd.write(chunk)
    return FileResponse(full_path_file, filename='Arquivos dos modelos de previsão de vazões diárias - PDP.zip')


handler = Mangum(app)
