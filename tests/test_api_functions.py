import pytest
from cryptomesh.dtos.functions_dto import FunctionCreateDTO, FunctionUpdateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from cryptomesh.dtos.storage_dto import StorageDTO, StorageUpdateDTO

@pytest.mark.asyncio
async def test_create_function(client):
    dto = FunctionCreateDTO(
        name="Test Function Create",
        microservice_id="ms_test_create",
        image="test:image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        storage=StorageDTO(
            capacity="10GB",
            storage_id="st_test_create",
            source_path="/local/path",
            sink_path="/remote/path"
        ),
        endpoint_id="ep_test_create",
        policy_id="Leo_Policy"
    )
    res = await client.post("/api/v1/functions/", json=dto.model_dump())
    assert res.status_code == 201
    data = res.json()
    assert data["function_id"] is not None
    assert data["name"] == dto.name
    assert data["image"] == dto.image
    assert data["resources"]["cpu"] == dto.resources.cpu
    assert data["resources"]["ram"] == dto.resources.ram
    assert data["storage"]["capacity"] == dto.storage.capacity
    assert data["endpoint_id"] == dto.endpoint_id

@pytest.mark.asyncio
async def test_get_function(client):
    dto = FunctionCreateDTO(
        name="Test Function Get",
        microservice_id="ms_test_get",
        image="get:image",
        resources=ResourcesDTO(cpu=1, ram="1GB"),
        storage=StorageDTO(
            capacity="5GB",
            storage_id="st_test_get",
            source_path="/local/get",
            sink_path="/remote/get"
        ),
        endpoint_id="ep_test_get",
        policy_id="Leo_Policy"
    )
    create_res = await client.post("/api/v1/functions/", json=dto.model_dump())
    function_id = create_res.json()["function_id"]

    get_res = await client.get(f"/api/v1/functions/{function_id}/")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["function_id"] == function_id
    assert data["name"] == dto.name
    assert data["endpoint_id"] == dto.endpoint_id

@pytest.mark.asyncio
async def test_update_function(client):
    create_dto = FunctionCreateDTO(
        name="Old Function",
        microservice_id="ms_test_update",
        image="old:image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        storage=StorageDTO(
            capacity="10GB",
            storage_id="st_update_old",
            source_path="/old/local",
            sink_path="/old/remote"
        ),
        endpoint_id="ep_test_update",
        policy_id="Old_Policy"
    )
    create_res = await client.post("/api/v1/functions/", json=create_dto.model_dump())
    function_id = create_res.json()["function_id"]

    update_dto = FunctionUpdateDTO(
        name="Updated Function",
        image="new:image",
        resources=ResourcesUpdateDTO(cpu=4),
        storage=StorageUpdateDTO(capacity="20GB"),
        deployment_status="deployed"
    )
    update_res = await client.put(f"/api/v1/functions/{function_id}/", json=update_dto.model_dump(exclude_unset=True))
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["name"] == update_dto.name
    assert data["image"] == update_dto.image
    assert data["resources"]["cpu"] == update_dto.resources.cpu
    assert data["storage"]["capacity"] == update_dto.storage.capacity
    assert data["deployment_status"] == update_dto.deployment_status

@pytest.mark.asyncio
async def test_delete_function(client):
    create_dto = FunctionCreateDTO(
        name="Delete Function",
        microservice_id="ms_test_delete",
        image="delete:image",
        resources=ResourcesDTO(cpu=1, ram="1GB"),
        storage=StorageDTO(
            capacity="5GB",
            storage_id="st_test_delete",
            source_path="/local/delete",
            sink_path="/remote/delete"
        ),
        endpoint_id="ep_test_delete",
        policy_id="Delete_Policy"
    )
    create_res = await client.post("/api/v1/functions/", json=create_dto.model_dump())
    function_id = create_res.json()["function_id"]

    delete_res = await client.delete(f"/api/v1/functions/{function_id}/")
    assert delete_res.status_code == 204

    get_res = await client.get(f"/api/v1/functions/{function_id}/")
    assert get_res.status_code == 404
