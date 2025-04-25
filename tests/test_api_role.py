import pytest

# ✅ TEST: Crear un nuevo rol correctamente
@pytest.mark.asyncio
async def test_create_role(client):
    payload = {
        "role_id": "role_test_create",
        "name": "Test Role",
        "description": "Role for testing",
        "permissions": ["read", "write"]
    }
    response = await client.post("/api/v1/roles/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Verificar que el ID del rol coincida
    assert data["role_id"] == payload["role_id"]
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["permissions"] == payload["permissions"]

# ✅ TEST: Intentar crear un rol duplicado debe fallar
@pytest.mark.asyncio
async def test_create_duplicate_role(client):
    payload = {
        "role_id": "role_test_duplicate",
        "name": "Duplicate Role",
        "description": "Duplicated role",
        "permissions": ["read", "write"]
    }
    # Crear inicialmente
    res1 = await client.post("/api/v1/roles/", json=payload)
    assert res1.status_code == 200
    # Intentar duplicar
    res2 = await client.post("/api/v1/roles/", json=payload)
    assert res2.status_code == 400

# ✅ TEST: Obtener un rol existente por ID
@pytest.mark.asyncio
async def test_get_role(client):
    payload = {
        "role_id": "role_test_get",
        "name": "Get Role",
        "description": "Role to get",
        "permissions": ["read"]
    }
    # Crear el rol antes de obtenerlo
    await client.post("/api/v1/roles/", json=payload)

    response = await client.get(f"/api/v1/roles/{payload['role_id']}")
    assert response.status_code == 200
    data = response.json()
    # Validar campos importantes del rol
    assert data["role_id"] == payload["role_id"]
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert data["permissions"] == payload["permissions"]

# ✅ TEST: Actualizar un rol correctamente
@pytest.mark.asyncio
async def test_update_role(client):
    payload = {
        "role_id": "role_test_update",
        "name": "Old Role",
        "description": "Old description",
        "permissions": ["read"]
    }
    await client.post("/api/v1/roles/", json=payload)

    update_payload = {
        "role_id": "role_test_update",
        "name": "Updated Role",
        "description": "Updated description",
        "permissions": ["read", "write"]
    }
    response = await client.put(f"/api/v1/roles/{payload['role_id']}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    # Validar que todos los cambios se reflejen correctamente
    assert data["role_id"] == update_payload["role_id"]
    assert data["name"] == update_payload["name"]
    assert data["description"] == update_payload["description"]
    assert data["permissions"] == update_payload["permissions"]

# ✅ TEST: Eliminar un rol y confirmar que ya no exista
@pytest.mark.asyncio
async def test_delete_role(client):
    payload = {
        "role_id": "role_test_delete",
        "name": "Role to Delete",
        "description": "Role that will be deleted",
        "permissions": ["read"]
    }
    await client.post("/api/v1/roles/", json=payload)

    # Eliminar rol
    delete_res = await client.delete(f"/api/v1/roles/{payload['role_id']}")
    assert delete_res.status_code == 200

    # Confirmar que ya no existe
    get_res = await client.get(f"/api/v1/roles/{payload['role_id']}")
    assert get_res.status_code == 404
