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
async def test_create_microservice(client):
    payload = {
        "microservice_id": "ms_test",
        "service_id": "s_test",
        "functions": ["fn1", "fn2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    response = await client.post("/api/v1/microservices/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["microservice_id"] == payload["microservice_id"]

# Test: Create duplicate Function should return error
@pytest.mark.asyncio
async def test_create_duplicate_microservice(client):
    payload = {
        "microservice_id": "ms_tests",
        "service_id": "s_tests",
        "functions": ["fn1", "fn3"],
        "resources": {"cpu": 4, "ram": "4GB"},
        "policy_id": "Leo_Policys"
    }
    # Create initially
    response = await client.post("/api/v1/microservices/", json=payload)
    assert response.status_code == 200
    # Try duplicate insert
    response_dup = await client.post("/api/v1/microservices/", json=payload)
    assert response_dup.status_code == 400

@pytest.mark.asyncio
async def test_get_microservice(client):
    payload = {
        "microservice_id": "ms_get",
        "service_id": "s_test",
        "functions": ["fn1", "fn2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/microservices/", json=payload)
    assert create_res.status_code == 200

    response = await client.get(f"/api/v1/microservices/{payload['microservice_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["microservice_id"] == payload["microservice_id"]
    assert data["service_id"] == payload["service_id"]

@pytest.mark.asyncio
async def test_update_microservice(client):
    payload = {
        "microservice_id": "ms_update",
        "service_id": "s_test",
        "functions": ["fn1", "fn2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/microservices/", json=payload)
    assert create_res.status_code == 200

    update_payload = {
        "microservice_id": "ms_update",  
        "service_id": "s_test",          
        "functions": ["fn3", "fn4"],    
        "resources": {"cpu": 4, "ram": "4GB"},  
        "policy_id": "New_Policy"        
    }
    update_res = await client.put(f"/api/v1/microservices/{payload['microservice_id']}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["microservice_id"] == update_payload["microservice_id"]
    assert data["functions"] == update_payload["functions"]
    assert data["resources"] == update_payload["resources"]
    assert data.get("policy_id") == update_payload["policy_id"]

@pytest.mark.asyncio
async def test_delete_microservice(client):
    payload = {
        "microservice_id": "ms_delete",
        "service_id": "s_test",
        "functions": ["fn1", "fn2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    create_res = await client.post("/api/v1/microservices/", json=payload)
    assert create_res.status_code == 200

    delete_res = await client.delete(f"/api/v1/microservices/{payload['microservice_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/microservices/{payload['microservice_id']}")
    assert get_res.status_code == 404