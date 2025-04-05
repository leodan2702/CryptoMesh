import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from cryptomesh.server import app


@pytest.mark.asyncio
async def test_get_services():
    async with AsyncClient(base_url="http://localhost:19000") as ac:
        response = await ac.get("/api/v1/services")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
