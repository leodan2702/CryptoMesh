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
async def test_create_endpoint(client):
    payload = {
        "endpoint_id": "ep_test",
        "name": "Test Endpoint",
        "image": "test_image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "security_policy": "security_manager",
        "policy_id": "Leo_Policy"
    }
    response = await client.post("/api/v1/endpoints/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Se verifica que se hayan incluido todos los campos del modelo
    assert data["endpoint_id"] == payload["endpoint_id"]
    assert data["name"] == payload["name"]
    assert data["image"] == payload["image"]
    assert data["resources"] == payload["resources"]
    assert data["security_policy"] == payload["security_policy"]
    assert data.get("policy_id") == payload["policy_id"]

# Test: Create duplicate Endpoint should return error
@pytest.mark.asyncio
async def test_create_duplicate_endpoint(client):
    payload = {
        "endpoint_id": "dup_state",
        "name": "ep1",
        "image": "test_images",
        "resources": {"cpu": 4, "ram": "4GB"},
        "security_policy": "security_managers",
        "policy_id": "Leo_Policys"
    }
    # Create initially
    response = await client.post("/api/v1/endpoints/", json=payload)
    assert response.status_code == 200
    # Try duplicate insert
    response_dup = await client.post("/api/v1/endpoints/", json=payload)
    assert response_dup.status_code == 400

@pytest.mark.asyncio
async def test_get_endpoint(client):
    # Primero, crea la política de seguridad necesaria
    policy_payload = {
        "sp_id": "security_manager",
        "roles": ["security_manager"],
        "requires_authentication": True,
        "policy_id": "Leo_Policy"
    }
    policy_res = await client.post("/api/v1/security-policies/", json=policy_payload)
    assert policy_res.status_code == 200

    # Luego, crea el endpoint que hace referencia a esa política
    payload = {
        "endpoint_id": "ep_get",
        "name": "Get Endpoint",
        "image": "test_image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "security_policy": "security_manager",
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/endpoints/", json=payload)
    assert create_res.status_code == 200

    response = await client.get(f"/api/v1/endpoints/{payload['endpoint_id']}")
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data["endpoint_id"] == payload["endpoint_id"]
    assert data["name"] == payload["name"]
    assert data["image"] == payload["image"]
    assert data["resources"] == payload["resources"]
    assert data["security_policy"] == payload["security_policy"]
    assert data.get("policy_id") == payload["policy_id"]

@pytest.mark.asyncio
async def test_update_endpoint(client):
    # Crear endpoint con todos los campos
    payload = {
        "endpoint_id": "ep_update",
        "name": "Old Endpoint",
        "image": "old_image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "security_policy": "security_manager",
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/endpoints/", json=payload)
    assert create_res.status_code == 200

    # En la actualización se envía un objeto completo con todos los campos actualizados
    update_payload = {
        "endpoint_id": "ep_update",  # Se mantiene el mismo ID
        "name": "Updated Endpoint",
        "image": "updated_image",
        "resources": {"cpu": 4, "ram": "4GB"},
        "security_policy": "ml1_analyst",
        "policy_id": "New_Policy"
    }
    update_res = await client.put(f"/api/v1/endpoints/{payload['endpoint_id']}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    # Verificar que se actualizó todo el objeto
    assert data["endpoint_id"] == update_payload["endpoint_id"]
    assert data["name"] == update_payload["name"]
    assert data["image"] == update_payload["image"]
    assert data["resources"] == update_payload["resources"]
    assert data["security_policy"] == update_payload["security_policy"]
    assert data.get("policy_id") == update_payload["policy_id"]

@pytest.mark.asyncio
async def test_delete_endpoint(client):
    payload = {
        "endpoint_id": "ep_delete",
        "name": "To Delete Endpoint",
        "image": "delete_image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "security_policy": "security_manager",
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/endpoints/", json=payload)
    assert create_res.status_code == 200

    delete_res = await client.delete(f"/api/v1/endpoints/{payload['endpoint_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/endpoints/{payload['endpoint_id']}")
    assert get_res.status_code == 404
