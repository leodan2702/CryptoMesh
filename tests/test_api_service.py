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
async def test_create_service(client):
    payload = {
         "service_id": "s_test",
         "security_policy": "security_manager",
         "microservices": ["MS1", "MS2"],
         "resources": {"cpu": 2, "ram": "2GB"},
         "policy_id": "Leo_Policy"
    }
    response = await client.post("/api/v1/services/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["service_id"] == payload["service_id"]
    assert data["security_policy"] == payload["security_policy"]
    assert data["resources"] == payload["resources"]

# Test: Create duplicate Function should return error
@pytest.mark.asyncio
async def test_create_duplicate_service(client):
    payload = {
         "service_id": "s_tests",
         "security_policy": "security_managers",
         "microservices": [],
         "resources": {"cpu": 4, "ram": "4GB"},
         "policy_id": "Leo_Policys"
    }
    # Create initially
    response = await client.post("/api/v1/services/", json=payload)
    assert response.status_code == 200
    # Try duplicate insert
    response_dup = await client.post("/api/v1/services/", json=payload)
    assert response_dup.status_code == 400

@pytest.mark.asyncio
async def test_get_service(client):
    payload = {
         "service_id": "s_get",
         "security_policy": "security_manager",
         "microservices": [],
         "resources": {"cpu": 2, "ram": "2GB"},
         "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/services/", json=payload)
    assert create_res.status_code == 200

    response = await client.get(f"/api/v1/services/{payload['service_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["service_id"] == payload["service_id"]
    assert data["security_policy"] == payload["security_policy"]

@pytest.mark.asyncio
async def test_update_service(client):
    payload = {
         "service_id": "s_update",
         "security_policy": "security_manager",
         "microservices": [],
         "resources": {"cpu": 2, "ram": "2GB"},
         "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/services/", json=payload)
    assert create_res.status_code == 200

    update_payload = {
         "service_id": "s_update",           
         "security_policy": "ml1_analyst",     
         "microservices": [],                 
         "resources": {"cpu": 4, "ram": "4GB"}, 
         "policy_id": "New_Policy"             
    }
    update_res = await client.put(f"/api/v1/services/{payload['service_id']}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["service_id"] == update_payload["service_id"]
    assert data["security_policy"] == update_payload["security_policy"]
    assert data["resources"] == update_payload["resources"]
    assert data.get("policy_id") == update_payload["policy_id"]

@pytest.mark.asyncio
async def test_delete_service(client):
    payload = {
         "service_id": "s_delete",
         "security_policy": "security_manager",
         "microservices": [],
         "resources": {"cpu": 2, "ram": "2GB"},
         "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/services/", json=payload)
    assert create_res.status_code == 200

    delete_res = await client.delete(f"/api/v1/services/{payload['service_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/services/{payload['service_id']}")
    assert get_res.status_code == 404
