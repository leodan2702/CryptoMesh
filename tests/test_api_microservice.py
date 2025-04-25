import pytest

# ✅ TEST: Crear un nuevo microservicio correctamente
@pytest.mark.asyncio
async def test_create_microservice(client):
    payload = {
        "microservice_id": "ms_test_create",
        "service_id": "s_test_create",
        "functions": ["fn1", "fn2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    response = await client.post("/api/v1/microservices/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Validar que el ID coincida
    assert data["microservice_id"] == payload["microservice_id"]
    assert data["service_id"] == payload["service_id"]
    assert data["functions"] == payload["functions"]
    assert data["resources"] == payload["resources"]
    assert data["policy_id"] == payload["policy_id"]

# ✅ TEST: Intentar crear un microservicio duplicado debe fallar
@pytest.mark.asyncio
async def test_create_duplicate_microservice(client):
    payload = {
        "microservice_id": "ms_test_duplicate",
        "service_id": "s_test_duplicate",
        "functions": ["fn1", "fn3"],
        "resources": {"cpu": 4, "ram": "4GB"},
        "policy_id": "Leo_Policy"
    }
    res1 = await client.post("/api/v1/microservices/", json=payload)
    assert res1.status_code == 200
    res2 = await client.post("/api/v1/microservices/", json=payload)
    assert res2.status_code == 400

# ✅ TEST: Obtener un microservicio existente por ID
@pytest.mark.asyncio
async def test_get_microservice(client):
    payload = {
        "microservice_id": "ms_test_get",
        "service_id": "s_test_get",
        "functions": ["fn1", "fn2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    await client.post("/api/v1/microservices/", json=payload)

    response = await client.get(f"/api/v1/microservices/{payload['microservice_id']}")
    assert response.status_code == 200
    data = response.json()
    # Validar campos claves
    assert data["microservice_id"] == payload["microservice_id"]
    assert data["service_id"] == payload["service_id"]
    assert data["functions"] == payload["functions"]
    assert data["resources"] == payload["resources"]
    assert data["policy_id"] == payload["policy_id"]

# ✅ TEST: Actualizar un microservicio correctamente
@pytest.mark.asyncio
async def test_update_microservice(client):
    payload = {
        "microservice_id": "ms_test_update",
        "service_id": "s_test_update",
        "functions": ["fn1", "fn2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    await client.post("/api/v1/microservices/", json=payload)

    update_payload = {
        "microservice_id": "ms_test_update",
        "service_id": "s_test_update",
        "functions": ["fn3", "fn4"],
        "resources": {"cpu": 4, "ram": "4GB"},
        "policy_id": "New_Policy"
    }
    update_res = await client.put(f"/api/v1/microservices/{payload['microservice_id']}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    # Validar campos modificados
    assert data["microservice_id"] == update_payload["microservice_id"]
    assert data["functions"] == update_payload["functions"]
    assert data["resources"] == update_payload["resources"]
    assert data["policy_id"] == update_payload["policy_id"]

# ✅ TEST: Eliminar un microservicio y confirmar que no exista
@pytest.mark.asyncio
async def test_delete_microservice(client):
    payload = {
        "microservice_id": "ms_test_delete",
        "service_id": "s_test_delete",
        "functions": ["fn1", "fn2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    await client.post("/api/v1/microservices/", json=payload)

    delete_res = await client.delete(f"/api/v1/microservices/{payload['microservice_id']}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/microservices/{payload['microservice_id']}")
    assert get_res.status_code == 404
