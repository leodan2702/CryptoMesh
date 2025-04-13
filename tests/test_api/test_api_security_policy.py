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
async def test_create_security_policy(client):
    payload = {
        "sp_id": "security_managers",
        "roles": ["security_manager"],
        "requires_authentication": True
    }
    response = await client.post("/api/v1/security-policies/", json=payload)
    assert response.status_code == 200, f"Error:{response.json()}"
    data = response.json()
    assert data["sp_id"] == payload["sp_id"]
    assert data["roles"] == payload["roles"]
    assert data["requires_authentication"] == payload["requires_authentication"]

# Test: Create duplicate Function should return error
@pytest.mark.asyncio
async def test_create_duplicate_security_policy(client):
    payload = {
        "sp_id": "security_managerss",
        "roles": ["security_managers"],
        "requires_authentication": True
    }
    # Create initially
    response = await client.post("/api/v1/security-policies/", json=payload)
    assert response.status_code == 200
    # Try duplicate insert
    response_dup = await client.post("/api/v1/security-policies/", json=payload)
    assert response_dup.status_code == 400

@pytest.mark.asyncio
async def test_get_security_policy(client):
    payload = {
        "sp_id": "ml1_analyst",
        "roles": ["ml1_analyst"],
        "requires_authentication": True
    }
    create_res = await client.post("/api/v1/security-policies/", json=payload)
    assert create_res.status_code == 200

    response = await client.get(f"/api/v1/security-policies/{payload['sp_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["sp_id"] == payload["sp_id"]
    assert data["roles"] == payload["roles"]

@pytest.mark.asyncio
async def test_update_security_policy(client):
    payload = {
        "sp_id": "sp_update",
        "roles": ["security_manager"],
        "requires_authentication": True
    }
    create_res = await client.post("/api/v1/security-policies/", json=payload)
    assert create_res.status_code == 200

    update_payload = {
        "sp_id": "sp_update",
        "roles": ["ml1_analyst"],
        "requires_authentication": False
    }
    update_res = await client.put(f"/api/v1/security-policies/{payload['sp_id']}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["sp_id"] == update_payload["sp_id"]
    assert data["roles"] == update_payload["roles"]
    assert data["requires_authentication"] == update_payload["requires_authentication"]

@pytest.mark.asyncio
async def test_delete_security_policy(client):
    payload = {
        "sp_id": "sp_delete",
        "roles": ["temp_role"],
        "requires_authentication": False
    }
    create_res = await client.post("/api/v1/security-policies/", json=payload)
    assert create_res.status_code == 200

    delete_res = await client.delete(f"/api/v1/security-policies/{payload['sp_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/security-policies/{payload['sp_id']}")
    assert get_res.status_code == 404