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
async def test_create_role(client):
    payload = {
        "role_id": "role_test",
        "name": "Test Role",
        "description": "Role for testing",
        "permissions": ["read", "write"]
    }
    response = await client.post("/api/v1/roles/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["role_id"] == payload["role_id"]

# Test: Create duplicate Function should return error
@pytest.mark.asyncio
async def test_create_duplicate_roles(client):
    payload = {
        "role_id": "role_tests",
        "name": "Test Roles",
        "description": "Role for testings",
        "permissions": ["reads", "writes"]
    }
    # Create initially
    response = await client.post("/api/v1/roles/", json=payload)
    assert response.status_code == 200
    # Try duplicate insert
    response_dup = await client.post("/api/v1/roles/", json=payload)
    assert response_dup.status_code == 400

@pytest.mark.asyncio
async def test_get_role(client):
    payload = {
        "role_id": "role_get",
        "name": "Get Role",
        "description": "Role to get",
        "permissions": ["read"]
    }
    create_res = await client.post("/api/v1/roles/", json=payload)
    assert create_res.status_code == 200

    response = await client.get(f"/api/v1/roles/{payload['role_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["role_id"] == payload["role_id"]
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["permissions"] == payload["permissions"]

@pytest.mark.asyncio
async def test_update_role(client):
    payload = {
        "role_id": "role_update",
        "name": "Old Role",
        "description": "Old description",
        "permissions": ["read"]
    }
    create_res = await client.post("/api/v1/roles/", json=payload)
    assert create_res.status_code == 200

    update_payload = {
        "role_id": "role_update",  # Se mantiene el mismo ID
        "name": "Updated Role",
        "description": "Updated description",
        "permissions": ["read", "write"]
    }
    update_res = await client.put(f"/api/v1/roles/{payload['role_id']}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["role_id"] == update_payload["role_id"]
    assert data["name"] == update_payload["name"]
    assert data["description"] == update_payload["description"]
    assert data["permissions"] == update_payload["permissions"]

@pytest.mark.asyncio
async def test_delete_role(client):
    payload = {
        "role_id": "role_delete",
        "name": "Role to Delete",
        "description": "Role that will be deleted",
        "permissions": ["read"]
    }
    create_res = await client.post("/api/v1/roles/", json=payload)
    assert create_res.status_code == 200

    delete_res = await client.delete(f"/api/v1/roles/{payload['role_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/roles/{payload['role_id']}")
    assert get_res.status_code == 404
