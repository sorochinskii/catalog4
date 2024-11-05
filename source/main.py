from api.v1.app import app as app_v1
from config import settings
from fastapi import FastAPI

app = FastAPI(title='Catalog4')

app.mount('/v1', app_v1)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('__main__:app',
                host=f'{settings.HOST}',
                port=settings.HTTP_PORT,
                reload=True,
                reload_dirs=['source'],
                log_level='debug')
