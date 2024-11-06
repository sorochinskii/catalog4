from config import settings
from fastapi import APIRouter, FastAPI
from utils import URLBuilder

url_builder = URLBuilder(
    host=settings.HOST,
    protocol=settings.HTTP_SECURE,
    port=settings.HTTP_PORT)
url = url_builder.url()
tags_metadata = [
    {
        'name': 'v1',
        "description": "API version 1",
        'externalDocs': {
            'description': 'sub-docs',
            'url': url
        }
    },
]

app = FastAPI(openapi_tags=tags_metadata)
