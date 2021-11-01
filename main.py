import os
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from mangum import Mangum
from datetime import datetime
import boto3
import requests


# Global Variables
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('ons_webhook')


stage = os.environ.get('STAGE', None)
root_path = f"/{stage}" if stage else "/"


app = FastAPI(title="serverless-app", root_path=root_path)


app.add_middleware(GZipMiddleware, minimum_size=1000)


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
    url = response.get('url')
    return url


def generate_stream_response(rsp, filename):
    return StreamingResponse(
        rsp.iter_content(chunk_size=1000),
        media_type="application/x-zip-compressed",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.zip",
            "Content-Encoding": "gzip"
        }
    )


def perform_http_stream(url):
    try:
        rsp = requests.get(url, stream=True)
        if rsp.status_code == 200:
            return generate_stream_response(rsp, 'Arquivos dos modelos de previsão de vazões diárias - PDP')
        else:
            return {'msg': f'oops could not process the request status code is : {rsp.status_code} url used {url}'}
    except requests.exceptions.HTTPError as e:
        print(e)
        return {'msg': 'oops an error has ocurred check logs'}


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
    return item


@app.get("/satellite_precipitation_history_zip")
def satellite_precipitation_history_zip():
    key = 'Histórico de Precipitação por Satélite'
    url = get_url_nome(key)
    if not url:
        return {'msg': f'error, failed try to get url from {key} in dynamodb'}
    return perform_http_stream(url)


@app.get("/hydraulic_operation_reports")
def hydraulic_operation_reports():
    key = 'Informes sobre a operação Hidráulica'
    url = get_url_nome(key)
    if not url:
        return {'msg': f'error, failed try to get url from {key} in dynamodb'}
    return perform_http_stream(url)


@app.get("/daily_flow_forecast_zip")
def daily_flow_forecast_zip():
    key = 'Arquivos dos modelos de previsão de vazões diárias - PDP'
    url = get_url_nome(key)
    if not url:
        return {'msg': f'error, failed try to get url from {key} in dynamodb'}
    return perform_http_stream(url)


@app.get("/entry_exit_dectks_dessem_zip")
def entry_exit_dectks_dessem_zip():
    key = 'Decks de entrada e saída - Modelo DESSEM'
    url = get_url_nome(key)
    if not url:
        return {'msg': f'error, failed try to get url from {key} in dynamodb'}
    return perform_http_stream(url)


handler = Mangum(app)


def handler(event, context):
    asgi_handler = Mangum(app)
    response = asgi_handler(event, context)
    return response
