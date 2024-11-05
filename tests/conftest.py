import asyncio
from typing import AsyncIterator, Generator

import pytest
from httpx import AsyncClient
from main import app
from starlette.testclient import TestClient


@pytest.fixture(scope='session')
def event_loop(request):
    '''Для решения проблемы ScopeMismatch: "You tried to access 
    the 'function' scoped fixture 'event_loop' with a 'module' 
    scoped request object, involved factories."
    Create an instance of the default event loop for each test case.'''
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_client_() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def test_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(app=app, base_url='http://testserver') as client:
        yield client
