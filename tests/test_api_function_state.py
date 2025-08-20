import pytest
from cryptomesh.dtos.function_state_dto import FunctionStateCreateDTO, FunctionStateUpdateDTO

# ───────────────────────────────
# ✅ TEST: Crear un nuevo estado de función
# ───────────────────────────────
@pytest.mark.asyncio
async def test_create_function_state(client):
    payload = {
        "function_id": "fs_test_create",
        "state": "pending",
        "metadata": {"info": "initial"}
    }
    response = await client.post("/api/v1/function-states/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "state_id" in data
    assert data["function_id"] == payload["function_id"]
    assert data["state"] == payload["state"]
    assert data["metadata"] == payload["metadata"]

# ───────────────────────────────
# ✅ TEST: Intentar crear un estado duplicado
# ───────────────────────────────
@pytest.mark.asyncio
async def test_create_duplicate_function_state(client):
    payload = {
        "function_id": "fs_test_duplicate",
        "state": "pending",
        "metadata": {"info": "initial"}
    }
    res1 = await client.post("/api/v1/function-states/", json=payload)
    assert res1.status_code == 201
    
    res2 = await client.post("/api/v1/function-states/", json=payload)
    # La API permite duplicados, entonces también será 201
    assert res2.status_code == 201


# ───────────────────────────────
# ✅ TEST: Obtener un estado existente por ID
# ───────────────────────────────
@pytest.mark.asyncio
async def test_get_function_state(client):
    payload = {
        "function_id": "fs_test_get",
        "state": "completed",
        "metadata": {"result": "success"}
    }
    create_res = await client.post("/api/v1/function-states/", json=payload)
    assert create_res.status_code == 201
    state_id = create_res.json()["state_id"]

    response = await client.get(f"/api/v1/function-states/{state_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["state_id"] == state_id
    assert data["function_id"] == payload["function_id"]
    assert data["state"] == payload["state"]
    assert data["metadata"] == payload["metadata"]

# ───────────────────────────────
# ✅ TEST: Actualizar un estado de función existente
# ───────────────────────────────
@pytest.mark.asyncio
async def test_update_function_state(client):
    payload = {
        "function_id": "fs_test_update",
        "state": "pending",
        "metadata": {"info": "initial"}
    }
    create_res = await client.post("/api/v1/function-states/", json=payload)
    assert create_res.status_code == 201
    state_id = create_res.json()["state_id"]

    update_payload = {
        "state": "running",
        "metadata": {"info": "in progress"}
    }
    response = await client.put(f"/api/v1/function-states/{state_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["state_id"] == state_id
    assert data["function_id"] == payload["function_id"]
    assert data["state"] == update_payload["state"]
    assert data["metadata"] == update_payload["metadata"]

# ───────────────────────────────
# ✅ TEST: Eliminar un estado y confirmar que ya no existe
# ───────────────────────────────
@pytest.mark.asyncio
async def test_delete_function_state(client):
    payload = {
        "function_id": "fs_test_delete",
        "state": "failed",
        "metadata": {"error": "timeout"}
    }
    create_res = await client.post("/api/v1/function-states/", json=payload)
    assert create_res.status_code == 201
    state_id = create_res.json()["state_id"]

    del_res = await client.delete(f"/api/v1/function-states/{state_id}")
    assert del_res.status_code == 204

    get_res = await client.get(f"/api/v1/function-states/{state_id}")
    assert get_res.status_code == 404

