import os
import sys
from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
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
root_path = f"/{stage}" if stage else "/"


app = FastAPI(title="serverless-app", root_path=root_path)


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


def get_url_nome(key):
    response = table.get_item(Key={'nome': key})
    response = response['Item']
    print('this is the response', response)
    return response


def generate_stream_response(rsp, filename):
    response = StreamingResponse(rsp.iter_content(
        chunk_size=1000), media_type="application/x-zip-compressed")
    response.headers["Content-Disposition"] = f'attachment; filename={filename}.zip'
    return response


def perform_http_strem(url):
    try:
        rsp = requests.get(url, stream=True)
        if rsp.status_code == 200:
            return generate_stream_response(rsp, 'Arquivos dos modelos de previsão de vazões diárias - PDP')
        else:
            return {'msg': f'oops could not process the request status codei is : {rsp.status_code} url used {url}'}
    except requests.exceptions.HTTPError as e:
        print(e)
        return {'msg': 'oops a error has ocurred check logs it semees be httpError'}


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
    response = add_item(item.dict())
    print(response)
    return item


@app.get("/satellite_precipitation_history_zip")
def satellite_precipitation_history_zip():
    item = get_url_nome('Histórico de Precipitação por Satélite')
    print(item)
    url = 'https://apps08.ons.org.br/ONS.Sintegre.Proxy/webhook?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVUkwiOiJodHRwczovL3NpbnRlZ3JlLm9ucy5vcmcuYnIvc2l0ZXMvOS81MS9Qcm9kdXRvcy8yNzcvRFNfT05TXzExMjAyMV9SVjBEMzEuemlwIiwidXNlcm5hbWUiOiJyaWNhcmRvQGh1ZXp0ZWxlY29tLmNvbS5iciIsIm5vbWVQcm9kdXRvIjoiRGVja3MgZGUgZW50cmFkYSBlIHNhw61kYSAtIE1vZGVsbyBERVNTRU0iLCJJc0ZpbGUiOiJUcnVlIiwiaXNzIjoiaHR0cDovL2xvY2FsLm9ucy5vcmcuYnIiLCJhdWQiOiJodHRwOi8vbG9jYWwub25zLm9yZy5iciIsImV4cCI6MTYzNTY5OTAyMywibmJmIjoxNjM1NjEyMzgzfQ.KboEWhn8szKxht_VOXggFvcD7pWHPDXq_EjVV53ZPPs'
    return perform_http_strem(url)


@app.get("/hydraulic_operation_reports")
def hydraulic_operation_reports():
    url = 'https://apps08.ons.org.br/ONS.Sintegre.Proxy/webhook?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVUkwiOiJodHRwczovL3NpbnRlZ3JlLm9ucy5vcmcuYnIvc2l0ZXMvOS81MS9Qcm9kdXRvcy8yNzcvRFNfT05TXzExMjAyMV9SVjBEMzEuemlwIiwidXNlcm5hbWUiOiJyaWNhcmRvQGh1ZXp0ZWxlY29tLmNvbS5iciIsIm5vbWVQcm9kdXRvIjoiRGVja3MgZGUgZW50cmFkYSBlIHNhw61kYSAtIE1vZGVsbyBERVNTRU0iLCJJc0ZpbGUiOiJUcnVlIiwiaXNzIjoiaHR0cDovL2xvY2FsLm9ucy5vcmcuYnIiLCJhdWQiOiJodHRwOi8vbG9jYWwub25zLm9yZy5iciIsImV4cCI6MTYzNTY5OTAyMywibmJmIjoxNjM1NjEyMzgzfQ.KboEWhn8szKxht_VOXggFvcD7pWHPDXq_EjVV53ZPPs'
    return perform_http_strem(url)


@app.get("/daily_flow_forecast_zip")
def daily_flow_forecast_zip():
    url = 'https://apps08.ons.org.br/ONS.Sintegre.Proxy/webhook?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVUkwiOiJodHRwczovL3NpbnRlZ3JlLm9ucy5vcmcuYnIvc2l0ZXMvOS81MS9Qcm9kdXRvcy8yNzcvRFNfT05TXzExMjAyMV9SVjBEMzEuemlwIiwidXNlcm5hbWUiOiJyaWNhcmRvQGh1ZXp0ZWxlY29tLmNvbS5iciIsIm5vbWVQcm9kdXRvIjoiRGVja3MgZGUgZW50cmFkYSBlIHNhw61kYSAtIE1vZGVsbyBERVNTRU0iLCJJc0ZpbGUiOiJUcnVlIiwiaXNzIjoiaHR0cDovL2xvY2FsLm9ucy5vcmcuYnIiLCJhdWQiOiJodHRwOi8vbG9jYWwub25zLm9yZy5iciIsImV4cCI6MTYzNTY5OTAyMywibmJmIjoxNjM1NjEyMzgzfQ.KboEWhn8szKxht_VOXggFvcD7pWHPDXq_EjVV53ZPPs'
    return perform_http_strem(url)


@app.get("/entry_exit_dectks_dessem_zip")
def entry_exit_dectks_dessem_zip():
    url = 'https://apps08.ons.org.br/ONS.Sintegre.Proxy/webhook?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJVUkwiOiJodHRwczovL3NpbnRlZ3JlLm9ucy5vcmcuYnIvc2l0ZXMvOS81MS9Qcm9kdXRvcy8yNzcvRFNfT05TXzExMjAyMV9SVjBEMzEuemlwIiwidXNlcm5hbWUiOiJyaWNhcmRvQGh1ZXp0ZWxlY29tLmNvbS5iciIsIm5vbWVQcm9kdXRvIjoiRGVja3MgZGUgZW50cmFkYSBlIHNhw61kYSAtIE1vZGVsbyBERVNTRU0iLCJJc0ZpbGUiOiJUcnVlIiwiaXNzIjoiaHR0cDovL2xvY2FsLm9ucy5vcmcuYnIiLCJhdWQiOiJodHRwOi8vbG9jYWwub25zLm9yZy5iciIsImV4cCI6MTYzNTY5OTAyMywibmJmIjoxNjM1NjEyMzgzfQ.KboEWhn8szKxht_VOXggFvcD7pWHPDXq_EjVV53ZPPs'
    return perform_http_strem(url)


handler = Mangum(app)


def handler(event, context):
    print(event, context)
    asgi_handler = Mangum(app)
    response = asgi_handler(event, context)
    return response
