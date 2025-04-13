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
async def test_create_function(client):
    payload = {
        "function_id": "fn_test",
        "microservice_id": "ms_test",
        "image": "test:image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "storage": {
            "capacity": "10GB",
            "storage_id": "st_test",
            "source_path": "/local/path",
            "sink_path": "/remote/path"
        },
        "endpoint_id": "ep1",
        "deployment_status": "pending",
        "policy_id": "Leo_Policy"
    }
    response = await client.post("/api/v1/functions/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["function_id"] == payload["function_id"]

# Test: Create duplicate Function should return error
@pytest.mark.asyncio
async def test_create_duplicate_function(client):
    payload = {
        "function_id": "fn_tests",
        "microservice_id": "ms_tests",
        "image": "test:images",
        "resources": {"cpu": 4, "ram": "4GB"},
        "storage": {
            "capacity": "11GB",
            "storage_id": "st_tests",
            "source_path": "/local/paths",
            "sink_path": "/remote/paths"
        },
        "endpoint_id": "ep2",
        "deployment_status": "pendings",
        "policy_id": "Leo_Policys"
    }
    # Create initially
    response = await client.post("/api/v1/functions/", json=payload)
    assert response.status_code == 200
    # Try duplicate insert
    response_dup = await client.post("/api/v1/functions/", json=payload)
    assert response_dup.status_code == 400

@pytest.mark.asyncio
async def test_get_function(client):
    payload = {
        "function_id": "fn_get",
        "microservice_id": "ms_test",
        "image": "test:image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "storage": {
            "capacity": "10GB",
            "storage_id": "st_get",
            "source_path": "/local/path",
            "sink_path": "/remote/path"
        },
        "endpoint_id": "ep1",
        "deployment_status": "pending",
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/functions/", json=payload)
    assert create_res.status_code == 200

    response = await client.get(f"/api/v1/functions/{payload['function_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["function_id"] == payload["function_id"]

@pytest.mark.asyncio
async def test_update_function(client):
    payload = {
        "function_id": "fn_update",
        "microservice_id": "ms_test",
        "image": "test:image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "storage": {
            "capacity": "10GB",
            "storage_id": "st_update",
            "source_path": "/local/path",
            "sink_path": "/remote/path"
        },
        "endpoint_id": "ep1",
        "deployment_status": "pending",
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/functions/", json=payload)
    assert create_res.status_code == 200

    # Se define el update por completo, con todos los campos actualizados:
    update_payload = {
        "function_id": "fn_update",  # Generalmente el ID no se actualiza, pero se puede enviar para confirmar
        "microservice_id": "ms_updated",
        "image": "updated:image",
        "resources": {"cpu": 4, "ram": "4GB"},
        "storage": {
            "capacity": "20GB",
            "storage_id": "st_updated",
            "source_path": "/updated/local/path",
            "sink_path": "/updated/remote/path"
        },
        "endpoint_id": "ep_updated",
        "deployment_status": "deployed",
        "policy_id": "Leo_Policy_Updated"
    }
    update_res = await client.put(f"/api/v1/functions/{payload['function_id']}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["microservice_id"] == "ms_updated"
    assert data["image"] == "updated:image"
    assert data["resources"] == {"cpu": 4, "ram": "4GB"}
    assert data["storage"] == {
        "capacity": "20GB",
        "storage_id": "st_updated",
        "source_path": "/updated/local/path",
        "sink_path": "/updated/remote/path"
    }
    assert data["endpoint_id"] == "ep_updated"
    assert data["deployment_status"] == "deployed"
    assert data["policy_id"] == "Leo_Policy_Updated"

@pytest.mark.asyncio
async def test_delete_function(client):
    payload = {
        "function_id": "fn_delete",
        "microservice_id": "ms_test",
        "image": "test:image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "storage": {
            "capacity": "10GB",
            "storage_id": "st_delete",
            "source_path": "/local/path",
            "sink_path": "/remote/path"
        },
        "endpoint_id": "ep1",
        "deployment_status": "pending",
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/functions/", json=payload)
    assert create_res.status_code == 200

    delete_res = await client.delete(f"/api/v1/functions/{payload['function_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/functions/{payload['function_id']}")
    assert get_res.status_code == 404