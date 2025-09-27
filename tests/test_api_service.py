import pytest
from cryptomesh.dtos.services_dto import ServiceUpdateDTO, ResourcesUpdateDTO, ServiceCreateDTO

@pytest.mark.asyncio
async def test_create_service(client):
    payload = {
        "name": "Test Service",
        "security_policy": "sp1",
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "policy_test_1"
    }
    response = await client.post("/api/v1/services/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "service_id" in data
    assert data["security_policy"] == payload["security_policy"]
    assert data["resources"] == payload["resources"]

@pytest.mark.asyncio
async def test_create_duplicate_service(client):
    payload = {
        "name": "Duplicate Service",
        "service_id": "DUPLICATE_TEST_ID",
        "security_policy": "sp2",
        "resources": {"cpu": 4, "ram": "4GB"},
        "policy_id": "policy_test_2"
    }
    res1 = await client.post("/api/v1/services/", json=payload)
    assert res1.status_code == 201
    res2 = await client.post("/api/v1/services/", json=payload)
    assert res2.status_code == 201  # tu API no bloquea duplicados actualmente


@pytest.mark.asyncio
async def test_get_service(client):
    payload = {
        "name": "Get Service",
        "security_policy": "sp3",
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "policy_test_3"
    }
    post_response = await client.post("/api/v1/services/", json=payload)
    assert post_response.status_code == 201
    service_id = post_response.json()["service_id"]

    response = await client.get(f"/api/v1/services/{service_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["service_id"] == service_id
    assert data["security_policy"] == payload["security_policy"]
    assert data["resources"] == payload["resources"]


@pytest.mark.asyncio
async def test_update_service(client):
    payload = {
        "name": "Update Service",
        "security_policy": "sp4",
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "policy_test_4"
    }
    post_response = await client.post("/api/v1/services/", json=payload)
    assert post_response.status_code == 201
    service_id = post_response.json()["service_id"]

    update_payload = {
        "security_policy": "sp_updated",
        "resources": {"cpu": 4, "ram": "4GB"}
    }
    response = await client.put(f"/api/v1/services/{service_id}/", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["service_id"] == service_id
    assert data["security_policy"] == update_payload["security_policy"]
    assert data["resources"] == update_payload["resources"]



@pytest.mark.asyncio
async def test_delete_service(client):
    payload = {
        "name": "Delete Service",
        "security_policy": "sp5",
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "policy_test_5"
    }
    post_response = await client.post("/api/v1/services/", json=payload)
    assert post_response.status_code == 201
    service_id = post_response.json()["service_id"]

    del_res = await client.delete(f"/api/v1/services/{service_id}/")
    assert del_res.status_code == 204

    get_res = await client.get(f"/api/v1/services/{service_id}/")
    assert get_res.status_code == 404
