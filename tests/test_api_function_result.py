import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from cryptomesh.server import app
from cryptomesh.db import connect_to_mongo

@pytest_asyncio.fixture(autouse=True)
async def setup_mongodb():
    await connect_to_mongo()

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_create_function_result(client):
    payload = {
        "state_id": "fr_test",
        "function_id": "fn_test",
        "metadata": {"output": "value"}
    }
    response = await client.post("/api/v1/function-results/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["state_id"] == payload["state_id"]

# Test: Create duplicate Function should return error
@pytest.mark.asyncio
async def test_create_duplicate_function_results(client):
    payload = {
        "state_id": "fr_tests",
        "function_id": "fn_tests",
        "metadata": {"output": "values"}
    }
    # Create initially
    response = await client.post("/api/v1/function-results/", json=payload)
    assert response.status_code == 200
    # Try duplicate insert
    response_dup = await client.post("/api/v1/function-results/", json=payload)
    assert response_dup.status_code == 400

@pytest.mark.asyncio
async def test_get_function_result(client):
    payload = {
        "state_id": "fr_get",
        "function_id": "fn_get",
        "metadata": {"result": "success"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 200

    response = await client.get(f"/api/v1/function-results/{payload['state_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["state_id"] == payload["state_id"]
    assert data["function_id"] == payload["function_id"]

@pytest.mark.asyncio
async def test_update_function_result(client):
    payload = {
        "state_id": "fr_update",
        "function_id": "fn_update",
        "metadata": {"status": "initial"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 200

    update_payload = {
        "state_id": "fr_update",  # Mantiene el mismo ID
        "function_id": "fn_update",
        "metadata": {"status": "updated", "detail": "complete update"}
    }
    update_res = await client.put(f"/api/v1/function-results/{payload['state_id']}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["state_id"] == update_payload["state_id"]
    assert data["function_id"] == update_payload["function_id"]
    assert data["metadata"] == update_payload["metadata"]

@pytest.mark.asyncio
async def test_delete_function_result(client):
    payload = {
        "state_id": "fr_delete",
        "function_id": "fn_delete",
        "metadata": {"error": "Timeout"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 200

    delete_res = await client.delete(f"/api/v1/function-results/{payload['state_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/function-results/{payload['state_id']}")
    assert get_res.status_code == 404
