import pytest
import httpx

@pytest.mark.asyncio
async def test_create_role(client):
    payload = {
        "name": "Test Role",
        "description": "Role for testing",
        "permissions": ["read", "write"]
    }
    response = await client.post("/api/v1/roles/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "role_id" in data
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["permissions"] == payload["permissions"]

@pytest.mark.asyncio
async def test_create_duplicate_role(client):
    payload = {
        "name": "Duplicate Role",
        "description": "Duplicated role",
        "permissions": ["read", "write"]
    }
    # Crear inicialmente
    res1 = await client.post("/api/v1/roles/", json=payload)
    assert res1.status_code == 201
    # Intentar duplicar
    res2 = await client.post("/api/v1/roles/", json=payload)
    # Ajusta según tu comportamiento real: 400 si duplicado, 201 si permite
    assert res2.status_code in (201, 400)

@pytest.mark.asyncio
async def test_get_role(client):
    payload = {
        "name": "Get Role",
        "description": "Role to get",
        "permissions": ["read"]
    }
    create_res = await client.post("/api/v1/roles/", json=payload)
    role_id = create_res.json()["role_id"]

    response = await client.get(f"/api/v1/roles/{role_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["role_id"] == role_id
    assert data["name"] == payload["name"]

@pytest.mark.asyncio
async def test_update_role(client):
    payload = {
        "name": "Old Role",
        "description": "Old description",
        "permissions": ["read"]
    }
    create_res = await client.post("/api/v1/roles/", json=payload)
    role_id = create_res.json()["role_id"]

    update_payload = {
        "name": "Updated Role",
        "description": "Updated description",
        "permissions": ["read", "write"]
    }

    response = await client.put(f"/api/v1/roles/{role_id}", json=update_payload)
    assert response.status_code == 200

    updated_data = response.json()
    assert updated_data["name"] == update_payload["name"]
    assert updated_data["description"] == update_payload["description"]
    assert updated_data["permissions"] == update_payload["permissions"]

@pytest.mark.asyncio
async def test_delete_role(client):
    payload = {
        "name": "Role to Delete",
        "description": "Role that will be deleted",
        "permissions": ["read"]
    }
    create_res = await client.post("/api/v1/roles/", json=payload)
    role_id = create_res.json()["role_id"]

    delete_res = await client.delete(f"/api/v1/roles/{role_id}")
    # FastAPI típicamente devuelve 204 No Content en DELETE
    assert delete_res.status_code == 204

    # Verificamos que ya no exista
    get_res = await client.get(f"/api/v1/roles/{role_id}")
    assert get_res.status_code == 404

