from httpx import AsyncClient


async def test_check_openapijson(test_client: AsyncClient):
    response = await test_client.get("/openapi.json")
    assert response.status_code == 200
