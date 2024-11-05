from config import settings
from fastapi import APIRouter, FastAPI

url = f'{settings.HTTP_SECURE}://{settings.HOST}:{settings.HTTP_PORT}/{settings.V1}/docs'

tags_metadata = [
    {
        'name': 'v1',
        "description": "API version 1",
        'externalDocs': {
            'description': 'sub-docs',
            # 'url': f'{settings.HTTP_SECURE}://{settings.HOST}:{settings.HTTP_PORT}/{settings.V1}/docs'
            'url': 'http://localhost:8446/v1/docs'
        }
    },
]

app = FastAPI(openapi_tags=tags_metadata)
