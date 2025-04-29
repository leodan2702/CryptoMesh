import pytest

# ✅ TEST: Crear un nuevo estado de endpoint
@pytest.mark.asyncio
async def test_create_endpoint_state(client):
    payload = {
        "state_id": "ep_state_create",
        "endpoint_id": "ep_test_create",
        "state": "warm",
        "metadata": {"info": "Testing create endpoint state"}
    }
    response = await client.post("/api/v1/endpoint-states/", json=payload)
    assert response.status_code == 201
    data = response.json()
    # Validar que el ID fue retornado correctamente
    assert data["state_id"] == payload["state_id"]
    assert data["endpoint_id"] == payload["endpoint_id"]
    assert data["state"] == payload["state"]
    assert data["metadata"] == payload["metadata"]

# ✅ TEST: Intentar duplicar un estado existente debe fallar
@pytest.mark.asyncio
async def test_create_duplicate_endpoint_state(client):
    payload = {
        "state_id": "ep_state_duplicate",
        "endpoint_id": "ep_test_duplicate",
        "state": "cold",
        "metadata": {"info": "first insert"}
    }
    res1 = await client.post("/api/v1/endpoint-states/", json=payload)
    assert res1.status_code == 201
    res2 = await client.post("/api/v1/endpoint-states/", json=payload)
    assert res2.status_code == 400

# ✅ TEST: Obtener un estado inexistente debe retornar 404
@pytest.mark.asyncio
async def test_get_nonexistent_endpoint_state(client):
    response = await client.get("/api/v1/endpoint-states/nonexistent_state")
    assert response.status_code == 404

# ✅ TEST: Actualizar un estado existente
@pytest.mark.asyncio
async def test_update_endpoint_state(client):
    payload = {
        "state_id": "ep_state_update",
        "endpoint_id": "ep_test_update",
        "state": "warm",
        "metadata": {"info": "initial"}
    }
    await client.post("/api/v1/endpoint-states/", json=payload)

    update_payload = {
        "state_id": "ep_state_update",
        "endpoint_id": "ep_test_update",
        "state": "cold",
        "metadata": {"info": "updated"}
    }
    update_res = await client.put(f"/api/v1/endpoint-states/{payload['state_id']}", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()

    # Validar que los campos fueron actualizados correctamente
    assert updated_data["state_id"] == update_payload["state_id"]
    assert updated_data["endpoint_id"] == update_payload["endpoint_id"]
    assert updated_data["state"] == update_payload["state"]
    assert updated_data["metadata"] == update_payload["metadata"]

# ✅ TEST: Eliminar un estado y confirmar que fue eliminado
@pytest.mark.asyncio
async def test_delete_endpoint_state(client):
    payload = {
        "state_id": "ep_state_delete",
        "endpoint_id": "ep_test_delete",
        "state": "warm",
        "metadata": {"info": "to be deleted"}
    }
    await client.post("/api/v1/endpoint-states/", json=payload)

    delete_res = await client.delete(f"/api/v1/endpoint-states/{payload['state_id']}")
    assert delete_res.status_code == 204

    get_res = await client.get(f"/api/v1/endpoint-states/{payload['state_id']}")
    assert get_res.status_code == 404
