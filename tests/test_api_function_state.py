import pytest

# ✅ TEST: Crear un nuevo estado de función
@pytest.mark.asyncio
async def test_create_function_state(client):
    payload = {
        "state_id": "fs_test_create",
        "function_id": "fn_test_create",
        "state": "pending",
        "metadata": {"info": "initial"}
    }
    response = await client.post("/api/v1/function-states/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Verifica que el estado fue creado correctamente
    assert data["state_id"] == payload["state_id"]
    assert data["function_id"] == payload["function_id"]
    assert data["state"] == payload["state"]
    assert data["metadata"] == payload["metadata"]

# ✅ TEST: Intentar crear un estado duplicado debe fallar
@pytest.mark.asyncio
async def test_create_duplicate_function_state(client):
    payload = {
        "state_id": "fs_test_duplicate",
        "function_id": "fn_test_duplicate",
        "state": "pending",
        "metadata": {"info": "initial"}
    }
    # Crear el estado una vez
    res1 = await client.post("/api/v1/function-states/", json=payload)
    assert res1.status_code == 200
    # Intentar duplicar
    res2 = await client.post("/api/v1/function-states/", json=payload)
    assert res2.status_code == 400

# ✅ TEST: Obtener un estado existente por ID
@pytest.mark.asyncio
async def test_get_function_state(client):
    payload = {
        "state_id": "fs_test_get",
        "function_id": "fn_test_get",
        "state": "completed",
        "metadata": {"result": "success"}
    }
    # Crear antes de obtener
    await client.post("/api/v1/function-states/", json=payload)

    response = await client.get(f"/api/v1/function-states/{payload['state_id']}")
    assert response.status_code == 200
    data = response.json()
    # Validar que se obtuvo correctamente
    assert data["state_id"] == payload["state_id"]
    assert data["function_id"] == payload["function_id"]
    assert data["state"] == payload["state"]
    assert data["metadata"] == payload["metadata"]

# ✅ TEST: Actualizar un estado de función existente
@pytest.mark.asyncio
async def test_update_function_state(client):
    state_id = "fs_test_update"

    # Paso 1: Crear el estado inicial
    payload = {
        "state_id": state_id,
        "function_id": "fn_test_update",
        "state": "pending",
        "metadata": {"info": "initial", "detail": "none"}
    }
    await client.post("/api/v1/function-states/", json=payload)

    # Paso 2: Actualizar con nuevos valores
    update_payload = {
        "state_id": state_id,
        "function_id": "fn_test_update",
        "state": "running",
        "metadata": {"info": "in progress", "detail": "updated"}
    }
    response = await client.put(f"/api/v1/function-states/{state_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()

    # Validar cambios
    assert data["state_id"] == update_payload["state_id"]
    assert data["function_id"] == update_payload["function_id"]
    assert data["state"] == update_payload["state"]
    assert data["metadata"] == update_payload["metadata"]

# ✅ TEST: Eliminar un estado y confirmar que ya no existe
@pytest.mark.asyncio
async def test_delete_function_state(client):
    state_id = "fs_test_delete"
    payload = {
        "state_id": state_id,
        "function_id": "fn_test_delete",
        "state": "failed",
        "metadata": {"error": "timeout"}
    }
    # Crear estado
    await client.post("/api/v1/function-states/", json=payload)

    # Eliminar estado
    del_res = await client.delete(f"/api/v1/function-states/{state_id}")
    assert del_res.status_code == 200

    # Confirmar que ya no existe
    get_res = await client.get(f"/api/v1/function-states/{state_id}")
    assert get_res.status_code == 404

