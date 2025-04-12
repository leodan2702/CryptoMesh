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
    transport = ASGITransport(app=app)  # Directly use your FastAPI app
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# Create an EndpointState
@pytest.mark.asyncio
async def test_create_endpoint_state(client):
    payload = {
        "state_id": "test_state_1",
        "endpoint_id": "ep1",
        "state": "warm",
        "metadata": {"info": "Testing create endpoint state"}
    }
    response = await client.post("/api/v1/endpoint-states/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["state_id"] == payload["state_id"]

# Test: Create duplicate EndpointState should return error
@pytest.mark.asyncio
async def test_create_duplicate_endpoint_state(client):
    payload = {
        "state_id": "dup_state",
        "endpoint_id": "ep1",
        "state": "cold",
        "metadata": {"info": "first insert"}
    }
    # Create initially
    response = await client.post("/api/v1/endpoint-states/", json=payload)
    assert response.status_code == 200
    # Try duplicate insert
    response_dup = await client.post("/api/v1/endpoint-states/", json=payload)
    assert response_dup.status_code == 400

# Test: Get EndpointState that does not exist
@pytest.mark.asyncio
async def test_get_nonexistent_endpoint_state(client):
    response = await client.get("/api/v1/endpoint-states/nonexistent_state")
    assert response.status_code == 404

# Test: Update an EndpointState
@pytest.mark.asyncio
async def test_update_endpoint_state(client):
    payload = {
        "state_id": "update_state",
        "endpoint_id": "ep1",
        "state": "warm",
        "metadata": {"info": "initial"}
    }
    # Create the record first
    create_res = await client.post("/api/v1/endpoint-states/", json=payload)
    assert create_res.status_code == 200

    # Update the state
    update_payload = {
        "state_id": "update_state",
        "endpoint_id": "ep1",
        "state": "cold",
        "metadata": {"info": "updated"}
    }
    update_res = await client.put(f"/api/v1/endpoint-states/{payload['state_id']}", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()
    assert updated_data["state"] == "cold"
    assert updated_data["metadata"]["info"] == "updated"

# Test: Delete an EndpointState
@pytest.mark.asyncio
async def test_delete_endpoint_state(client):
    payload = {
        "state_id": "delete_state",
        "endpoint_id": "ep1",
        "state": "warm",
        "metadata": {"info": "to be deleted"}
    }
    create_res = await client.post("/api/v1/endpoint-states/", json=payload)
    assert create_res.status_code == 200

    delete_res = await client.delete(f"/api/v1/endpoint-states/{payload['state_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/endpoint-states/{payload['state_id']}")
    assert get_res.status_code == 404
