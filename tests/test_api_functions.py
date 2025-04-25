import pytest

# ✅ TEST: Crear una función correctamente
@pytest.mark.asyncio
async def test_create_function(client):
    payload = {
        "function_id": "fn_test_create",
        "microservice_id": "ms_test_create",
        "image": "test:image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "storage": {
            "capacity": "10GB",
            "storage_id": "st_test_create",
            "source_path": "/local/path",
            "sink_path": "/remote/path"
        },
        "endpoint_id": "ep_test_create",
        "deployment_status": "pending",
        "policy_id": "Leo_Policy"
    }
    response = await client.post("/api/v1/functions/", json=payload)
    assert response.status_code == 200
    data = response.json()
    # Verificamos que el ID coincida
    assert data["function_id"] == payload["function_id"]
    assert data["microservice_id"] == payload["microservice_id"]
    assert data["image"] == payload["image"]
    assert data["resources"] == payload["resources"]
    assert data["storage"] == payload["storage"]
    assert data["endpoint_id"] == payload["endpoint_id"]
    assert data["deployment_status"] == payload["deployment_status"]
    assert data["policy_id"] == payload["policy_id"]

# ✅ TEST: Intentar crear una función duplicada
@pytest.mark.asyncio
async def test_create_duplicate_function(client):
    payload = {
        "function_id": "fn_test_duplicate",
        "microservice_id": "ms_test_duplicate",
        "image": "test:image",
        "resources": {"cpu": 4, "ram": "4GB"},
        "storage": {
            "capacity": "11GB",
            "storage_id": "st_test_duplicate",
            "source_path": "/local/dup",
            "sink_path": "/remote/dup"
        },
        "endpoint_id": "ep_test_duplicate",
        "deployment_status": "pending",
        "policy_id": "Leo_Policy"
    }
    res1 = await client.post("/api/v1/functions/", json=payload)
    assert res1.status_code == 200
    res2 = await client.post("/api/v1/functions/", json=payload)
    assert res2.status_code == 400

# ✅ TEST: Obtener una función existente
@pytest.mark.asyncio
async def test_get_function(client):
    payload = {
        "function_id": "fn_test_get",
        "microservice_id": "ms_test_get",
        "image": "test:image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "storage": {
            "capacity": "10GB",
            "storage_id": "st_test_get",
            "source_path": "/local/path",
            "sink_path": "/remote/path"
        },
        "endpoint_id": "ep_test_get",
        "deployment_status": "pending",
        "policy_id": "Leo_Policy"
    }
    await client.post("/api/v1/functions/", json=payload)

    response = await client.get(f"/api/v1/functions/{payload['function_id']}")
    assert response.status_code == 200
    data = response.json()
    assert data["function_id"] == payload["function_id"]
    assert data["microservice_id"] == payload["microservice_id"]
    assert data["image"] == payload["image"]
    assert data["resources"] == payload["resources"]
    assert data["storage"] == payload["storage"]
    assert data["endpoint_id"] == payload["endpoint_id"]
    assert data["deployment_status"] == payload["deployment_status"]
    assert data["policy_id"] == payload["policy_id"]

# ✅ TEST: Actualizar una función existente
@pytest.mark.asyncio
async def test_update_function(client):
    function_id = "fn_test_update"
    payload = {
        "function_id": function_id,
        "microservice_id": "ms_test_update_old",
        "image": "old:image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "storage": {
            "capacity": "10GB",
            "storage_id": "st_test_update_old",
            "source_path": "/old/local",
            "sink_path": "/old/remote"
        },
        "endpoint_id": "ep_test_update_old",
        "deployment_status": "pending",
        "policy_id": "Old_Policy"
    }
    await client.post("/api/v1/functions/", json=payload)

    updated_payload = {
        "function_id": function_id,
        "microservice_id": "ms_test_update_new",
        "image": "new:image",
        "resources": {"cpu": 4, "ram": "4GB"},
        "storage": {
            "capacity": "20GB",
            "storage_id": "st_test_update_new",
            "source_path": "/new/local",
            "sink_path": "/new/remote"
        },
        "endpoint_id": "ep_test_update_new",
        "deployment_status": "deployed",
        "policy_id": "New_Policy"
    }
    response = await client.put(f"/api/v1/functions/{function_id}", json=updated_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["microservice_id"] == updated_payload["microservice_id"]
    assert data["image"] == updated_payload["image"]
    assert data["resources"] == updated_payload["resources"]
    assert data["storage"] == updated_payload["storage"]
    assert data["endpoint_id"] == updated_payload["endpoint_id"]
    assert data["deployment_status"] == updated_payload["deployment_status"]
    assert data["policy_id"] == updated_payload["policy_id"]

# ✅ TEST: Eliminar una función y verificar que ya no exista
@pytest.mark.asyncio
async def test_delete_function(client):
    function_id = "fn_test_delete"
    payload = {
        "function_id": function_id,
        "microservice_id": "ms_test_delete",
        "image": "delete:image",
        "resources": {"cpu": 2, "ram": "2GB"},
        "storage": {
            "capacity": "10GB",
            "storage_id": "st_test_delete",
            "source_path": "/delete/local",
            "sink_path": "/delete/remote"
        },
        "endpoint_id": "ep_test_delete",
        "deployment_status": "pending",
        "policy_id": "Delete_Policy"
    }
    await client.post("/api/v1/functions/", json=payload)

    delete_res = await client.delete(f"/api/v1/functions/{function_id}")
    assert delete_res.status_code == 200

    get_res = await client.get(f"/api/v1/functions/{function_id}")
    assert get_res.status_code == 404
