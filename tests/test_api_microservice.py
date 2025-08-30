import pytest
from cryptomesh.dtos.microservices_dto import MicroserviceCreateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO

@pytest.mark.asyncio
async def test_create_microservice(client):
    dto = MicroserviceCreateDTO(
        service_id="s_test_create",
        functions=["fn1", "fn2"],
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    response = await client.post("/api/v1/microservices/", json=dto.model_dump())
    assert response.status_code == 201
    data = response.json()

    assert "microservice_id" in data
    assert data["service_id"] == dto.service_id
    assert data["functions"] == dto.functions
    assert data["resources"] == dto.resources.model_dump()


@pytest.mark.asyncio
async def test_list_microservices(client):
    response = await client.get("/api/v1/microservices/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)



@pytest.mark.asyncio
async def test_get_microservice(client):
    dto = MicroserviceCreateDTO(
        service_id="s_test_get",
        functions=["fn1", "fn2"],
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    create_res = await client.post("/api/v1/microservices/", json=dto.model_dump())
    assert create_res.status_code == 201
    microservice_id = create_res.json()["microservice_id"]

    get_res = await client.get(f"/api/v1/microservices/{microservice_id}/")
    assert get_res.status_code == 200
    data = get_res.json()

    assert data["microservice_id"] == microservice_id
    assert data["service_id"] == dto.service_id
    assert data["functions"] == dto.functions
    assert data["resources"] == dto.resources.model_dump()


@pytest.mark.asyncio
async def test_update_microservice(client):
    dto = MicroserviceCreateDTO(
        service_id="s_test_update",
        functions=["fn1", "fn2"],
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    create_res = await client.post("/api/v1/microservices/", json=dto.model_dump())
    microservice_id = create_res.json()["microservice_id"]

    update_payload = {
        "service_id": "s_test_update",
        "functions": ["fn3", "fn4"],
        "resources": {"cpu": 4, "ram": "4GB"},
        "policy_id": "New_Policy"
    }

    update_res = await client.put(f"/api/v1/microservices/{microservice_id}/", json=update_payload)
    assert update_res.status_code == 200
    updated_data = update_res.json()

    assert updated_data["microservice_id"] == microservice_id
    assert updated_data["service_id"] == update_payload["service_id"]
    assert updated_data["functions"] == update_payload["functions"]
    assert updated_data["resources"] == update_payload["resources"]


@pytest.mark.asyncio
async def test_delete_microservice(client):
    dto = MicroserviceCreateDTO(
        service_id="s_test_delete",
        functions=["fn1", "fn2"],
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    create_res = await client.post("/api/v1/microservices/", json=dto.model_dump())
    microservice_id = create_res.json()["microservice_id"]

    delete_res = await client.delete(f"/api/v1/microservices/{microservice_id}/")
    assert delete_res.status_code == 204

    # Confirmamos que ya no existe
    get_res = await client.get(f"/api/v1/microservices/{microservice_id}/")
    assert get_res.status_code == 404
