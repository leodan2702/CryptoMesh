import pytest

# ✅ TEST: Crear un nuevo servicio correctamente
@pytest.mark.asyncio
async def test_create_service(client):
    payload = {
        "service_id": "s_test_create",
        "security_policy": "security_manager",
        "microservices": ["MS1", "MS2"],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    response = await client.post("/api/v1/services/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Validar atributos clave
    assert data["service_id"] == payload["service_id"]
    assert data["security_policy"] == payload["security_policy"]
    assert data["resources"] == payload["resources"]
    assert data["policy_id"] == payload["policy_id"]
    assert data["microservices"] == payload["microservices"]

# ✅ TEST: Crear un servicio duplicado debe fallar
@pytest.mark.asyncio
async def test_create_duplicate_service(client):
    payload = {
        "service_id": "s_test_duplicate",
        "security_policy": "security_manager",
        "microservices": [],
        "resources": {"cpu": 4, "ram": "4GB"},
        "policy_id": "Leo_Policy"
    }
    res1 = await client.post("/api/v1/services/", json=payload)
    assert res1.status_code == 200
    res2 = await client.post("/api/v1/services/", json=payload)
    assert res2.status_code == 400

# ✅ TEST: Obtener un servicio existente
@pytest.mark.asyncio
async def test_get_service(client):
    payload = {
        "service_id": "s_test_get",
        "security_policy": "security_manager",
        "microservices": [],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    await client.post("/api/v1/services/", json=payload)

    response = await client.get(f"/api/v1/services/{payload['service_id']}")
    assert response.status_code == 200
    data = response.json()
    # Validar valores esperados
    assert data["service_id"] == payload["service_id"]
    assert data["security_policy"] == payload["security_policy"]
    assert data["resources"] == payload["resources"]
    assert data["policy_id"] == payload["policy_id"]
    assert data["microservices"] == payload["microservices"]

# ✅ TEST: Actualizar un servicio correctamente
@pytest.mark.asyncio
async def test_update_service(client):
    payload = {
        "service_id": "s_test_update",
        "security_policy": "security_manager",
        "microservices": [],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    await client.post("/api/v1/services/", json=payload)

    update_payload = {
        "service_id": "s_test_update",
        "security_policy": "ml1_analyst",
        "microservices": ["MS3"],
        "resources": {"cpu": 4, "ram": "4GB"},
        "policy_id": "New_Policy"
    }
    response = await client.put(f"/api/v1/services/{payload['service_id']}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    # Verificar cambios reflejados
    assert data["service_id"] == update_payload["service_id"]
    assert data["security_policy"] == update_payload["security_policy"]
    assert data["resources"] == update_payload["resources"]
    assert data["policy_id"] == update_payload["policy_id"]
    assert data["microservices"] == update_payload["microservices"]

# ✅ TEST: Eliminar un servicio y confirmar que ya no existe
@pytest.mark.asyncio
async def test_delete_service(client):
    payload = {
        "service_id": "s_test_delete",
        "security_policy": "security_manager",
        "microservices": [],
        "resources": {"cpu": 2, "ram": "2GB"},
        "policy_id": "Leo_Policy"
    }
    await client.post("/api/v1/services/", json=payload)

    del_res = await client.delete(f"/api/v1/services/{payload['service_id']}")
    assert del_res.status_code == 200

    get_res = await client.get(f"/api/v1/services/{payload['service_id']}")
    assert get_res.status_code == 404
