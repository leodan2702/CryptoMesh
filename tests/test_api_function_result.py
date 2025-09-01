import pytest

# ✅ TEST: Crear un nuevo resultado de función
@pytest.mark.asyncio
async def test_create_function_result(client):
    payload = {
        "function_id": "fn_test",
        "metadata": {"output": "value"}
    }
    response = await client.post("/api/v1/function-results/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "result_id" in data
    assert data["function_id"] == payload["function_id"]
    assert data["metadata"] == payload["metadata"]

# ✅ TEST: Obtener un resultado por su result_id
@pytest.mark.asyncio
async def test_get_function_result(client):
    payload = {
        "function_id": "fn_get_test",
        "metadata": {"result": "success"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 201
    result_id = create_res.json()["result_id"]

    response = await client.get(f"/api/v1/function-results/{result_id}/")
    assert response.status_code == 200
    data = response.json()
    assert data["result_id"] == result_id
    assert data["function_id"] == payload["function_id"]
    assert data["metadata"] == payload["metadata"]

# ✅ TEST: Actualizar un resultado existente
@pytest.mark.asyncio
async def test_update_function_result(client):
    payload = {
        "function_id": "fn_update_test",
        "metadata": {"status": "initial"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 201
    result_id = create_res.json()["result_id"]

    update_payload = {
        "metadata": {"status": "updated", "detail": "full update"}
    }
    response = await client.put(f"/api/v1/function-results/{result_id}/", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result_id"] == result_id
    assert data["function_id"] == payload["function_id"]
    assert data["metadata"] == update_payload["metadata"]

# ✅ TEST: Eliminar un resultado y verificar su inexistencia
@pytest.mark.asyncio
async def test_delete_function_result(client):
    payload = {
        "function_id": "fn_delete_test",
        "metadata": {"error": "Timeout"}
    }
    create_res = await client.post("/api/v1/function-results/", json=payload)
    assert create_res.status_code == 201
    result_id = create_res.json()["result_id"]

    delete_res = await client.delete(f"/api/v1/function-results/{result_id}/")
    assert delete_res.status_code == 204

    get_res = await client.get(f"/api/v1/function-results/{result_id}/")
    assert get_res.status_code == 404
