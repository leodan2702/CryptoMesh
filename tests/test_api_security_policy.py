import pytest

# ✅ TEST: Crear una política de seguridad correctamente
@pytest.mark.asyncio
async def test_create_security_policy(client):
    payload = {
        "sp_id": "sp_test_create",
        "roles": ["security_manager"],
        "requires_authentication": True
    }
    response = await client.post("/api/v1/security-policies/", json=payload)
    assert response.status_code == 201, f"Error: {response.json()}"
    data = response.json()
    # Validar campos clave
    assert data["sp_id"] == payload["sp_id"]
    assert data["roles"] == payload["roles"]
    assert data["requires_authentication"] == payload["requires_authentication"]

# ✅ TEST: Intentar crear una política duplicada debe fallar
@pytest.mark.asyncio
async def test_create_duplicate_security_policy(client):
    payload = {
        "sp_id": "sp_test_duplicate",
        "roles": ["duplicate_role"],
        "requires_authentication": True
    }
    res1 = await client.post("/api/v1/security-policies/", json=payload)
    assert res1.status_code == 201
    res2 = await client.post("/api/v1/security-policies/", json=payload)
    assert res2.status_code == 400

# ✅ TEST: Obtener una política de seguridad existente
@pytest.mark.asyncio
async def test_get_security_policy(client):
    payload = {
        "sp_id": "sp_test_get",
        "roles": ["ml1_analyst"],
        "requires_authentication": True
    }
    await client.post("/api/v1/security-policies/", json=payload)

    response = await client.get(f"/api/v1/security-policies/{payload['sp_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["sp_id"] == payload["sp_id"]
    assert data["roles"] == payload["roles"]
    assert data["requires_authentication"] == payload["requires_authentication"]

# ✅ TEST: Actualizar una política de seguridad
@pytest.mark.asyncio
async def test_update_security_policy(client):
    payload = {
        "sp_id": "sp_test_update",
        "roles": ["security_manager"],
        "requires_authentication": True
    }
    await client.post("/api/v1/security-policies/", json=payload)

    update_payload = {
        "sp_id": "sp_test_update",
        "roles": ["ml1_analyst"],
        "requires_authentication": False
    }
    response = await client.put(f"/api/v1/security-policies/{payload['sp_id']}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    # Validar cambios
    assert data["sp_id"] == update_payload["sp_id"]
    assert data["roles"] == update_payload["roles"]
    assert data["requires_authentication"] == update_payload["requires_authentication"]

# ✅ TEST: Eliminar una política de seguridad y confirmar su eliminación
@pytest.mark.asyncio
async def test_delete_security_policy(client):
    payload = {
        "sp_id": "sp_test_delete",
        "roles": ["temp_role"],
        "requires_authentication": False
    }
    await client.post("/api/v1/security-policies/", json=payload)

    delete_res = await client.delete(f"/api/v1/security-policies/{payload['sp_id']}")
    assert delete_res.status_code == 204

    get_res = await client.get(f"/api/v1/security-policies/{payload['sp_id']}")
    assert get_res.status_code == 404
