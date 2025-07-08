import pytest

# ✅ TEST: Crear un nuevo resultado de función
@pytest.mark.asyncio
async def test_create_function_result(client):
    payload = {
        "state_id": "fr_test_create",
        "function_id": "fn_test",
        "metadata": {"output": "value"}
    }
    response = await client.post("/api/v1/function-results/", json=payload)
    assert response.status_code == 201  
    data = response.json()
    assert data["state_id"] == payload["state_id"]
    assert data["function_id"] == payload["function_id"]
    assert data["metadata"] == payload["metadata"]

# ✅ TEST: Crear resultado duplicado debe fallar
@pytest.mark.asyncio
async def test_create_duplicate_function_result(client):
    payload = {
        "state_id": "fr_duplicate",
        "function_id": "fn_duplicate",
        "metadata": {"output": "duplicate"}
    }
    response_1 = await client.post("/api/v1/function-results/", json=payload)
    assert response_1.status_code == 201 

    response_2 = await client.post("/api/v1/function-results/", json=payload)
    assert response_2.status_code == 400  

# ✅ TEST: Obtener un resultado por su state_id
@pytest.mark.asyncio
async def test_get_function_result(client):
    payload = {
        "state_id": "fr_get_test",
        "function_id": "fn_get_test",
        "metadata": {"result": "success"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 201

    response = await client.get(f"/api/v1/function-results/{payload['state_id']}")
    assert response.status_code == 200 
    data = response.json()
    assert data["state_id"] == payload["state_id"]
    assert data["function_id"] == payload["function_id"]
    assert data["metadata"] == payload["metadata"]

# ✅ TEST: Actualizar un resultado existente
@pytest.mark.asyncio
async def test_update_function_result(client):
    payload = {
        "state_id": "fr_update_test",
        "function_id": "fn_update_test",
        "metadata": {"status": "initial"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 201

    update_payload = {
        "state_id": payload["state_id"], 
        "function_id": payload["function_id"],
        "metadata": {"status": "updated", "detail": "full update"}
    }
    response = await client.put(f"/api/v1/function-results/{payload['state_id']}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["state_id"] == update_payload["state_id"]
    assert data["function_id"] == update_payload["function_id"]
    assert data["metadata"] == update_payload["metadata"]

# ✅ TEST: Eliminar un resultado y verificar su inexistencia
@pytest.mark.asyncio
async def test_delete_function_result(client):
    payload = {
        "state_id": "fr_delete_test",
        "function_id": "fn_delete_test",
        "metadata": {"error": "Timeout"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 201

    delete_res = await client.delete(f"/api/v1/function-results/{payload['state_id']}")
    assert delete_res.status_code == 204  

    get_res = await client.get(f"/api/v1/function-results/{payload['state_id']}")
    assert get_res.status_code == 404



