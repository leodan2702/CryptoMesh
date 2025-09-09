import pytest
from cryptomesh.dtos.functions_dto import FunctionCreateDTO, FunctionResponseDTO, FunctionUpdateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO
from cryptomesh.dtos.storage_dto import StorageDTO
from cryptomesh.services.functions_services import FunctionsService
from cryptomesh.repositories.functions_repository import FunctionsRepository
from cryptomesh.errors import NotFoundError


@pytest.mark.asyncio
async def test_create_function(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    storage = StorageDTO(
        capacity="10GB",
        source_path="/src",
        sink_path="/dst"
    )

    create_dto = FunctionCreateDTO(
        name="Test Function",
        microservice_id="ms-1",
        image="test_function_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        storage=storage,
        endpoint_id="ep-123",
        policy_id="policy-abc"
    )
    created = await service.create_function(create_dto.to_model())
    response_dto = FunctionResponseDTO.from_model(created)

    assert response_dto.function_id == created.function_id
    assert response_dto.name == "Test Function"
    assert response_dto.image == "test_function_image"
    assert response_dto.resources.cpu == 2
    assert response_dto.storage.capacity == "10GB"
    assert response_dto.storage.source_path == "/src"
    assert response_dto.storage.sink_path == "/dst"


@pytest.mark.asyncio
async def test_get_function(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    storage = StorageDTO(
        capacity="5GB",
        source_path="/src2",
        sink_path="/dst2"
    )

    create_dto = FunctionCreateDTO(
        name="Get Function",
        microservice_id="ms-2",
        image="get_function_image",
        resources=ResourcesDTO(cpu=1, ram="1GB"),
        storage=storage,
        endpoint_id="ep-456",
        policy_id="policy-def"
    )
    created = await service.create_function(create_dto.to_model())
    fetched = await service.get_function(created.function_id)
    response_dto = FunctionResponseDTO.from_model(fetched)

    assert response_dto.function_id == created.function_id
    assert response_dto.name == "Get Function"
    assert response_dto.image == "get_function_image"


@pytest.mark.asyncio
async def test_update_function(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    storage = StorageDTO(
        capacity="2GB",
        source_path="/src3",
        sink_path="/dst3"
    )

    create_dto = FunctionCreateDTO(
        name="Old Function",
        microservice_id="ms-3",
        image="old_function_image",
        resources=ResourcesDTO(cpu=1, ram="1GB"),
        storage=storage,
        endpoint_id="ep-789",
        policy_id="policy-ghi"
    )
    created = await service.create_function(create_dto.to_model())

    update_dto = FunctionUpdateDTO(
        name="Updated Function",
        image="updated_function_image",
        deployment_status="deployed"
    )

    updated_model = await service.update_function(
        created.function_id,
        update_dto.model_dump(exclude_unset=True)
    )
    response_dto = FunctionResponseDTO.from_model(updated_model)

    assert response_dto.name == "Updated Function"
    assert response_dto.image == "updated_function_image"
    assert response_dto.deployment_status == "deployed"


@pytest.mark.asyncio
async def test_delete_function(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    storage = StorageDTO(
        capacity="8GB",
        source_path="/src4",
        sink_path="/dst4"
    )

    create_dto = FunctionCreateDTO(
        name="Delete Function",
        microservice_id="ms-4",
        image="delete_function_image",
        resources=ResourcesDTO(cpu=2, ram="4GB"),
        storage=storage,
        endpoint_id="ep-000",
        policy_id="policy-jkl"
    )
    created = await service.create_function(create_dto.to_model())

    await service.delete_function(created.function_id)

    with pytest.raises(NotFoundError):
        await service.get_function(created.function_id)


@pytest.mark.asyncio
async def test_list_functions(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    for i in range(3):
        storage = StorageDTO(
            capacity=f"{i+1}GB",
            source_path=f"/src{i}",
            sink_path=f"/dst{i}"
        )
        create_dto = FunctionCreateDTO(
            name=f"Function {i}",
            microservice_id=f"ms-{i}",
            image=f"function_image_{i}",
            resources=ResourcesDTO(cpu=1, ram="1GB"),
            storage=storage,
            endpoint_id=f"ep-{i}",
            policy_id=f"policy-{i}"
        )
        await service.create_function(create_dto.to_model())

    functions = await service.list_functions()
    assert isinstance(functions, list)
    assert len(functions) >= 3
