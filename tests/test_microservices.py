import pytest
from cryptomesh.dtos.microservices_dto import (
    MicroserviceCreateDTO,
    MicroserviceResponseDTO,
    MicroserviceUpdateDTO
)
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.services.microservices_services import MicroservicesService
from cryptomesh.errors import NotFoundError

@pytest.mark.asyncio
async def test_create_microservice(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)
    service = MicroservicesService(repo)

    create_dto = MicroserviceCreateDTO(
        service_id="s_test_create",
        name="Test Microservice Create",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    created = await service.create_microservice(create_dto.to_model())
    response_dto = MicroserviceResponseDTO.from_model(created)

    assert response_dto.microservice_id == created.microservice_id
    assert response_dto.service_id == "s_test_create"
    assert response_dto.name == "Test Microservice Create"
    assert response_dto.resources.cpu == 2
    assert response_dto.resources.ram == "2GB"

@pytest.mark.asyncio
async def test_get_microservice(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)
    service = MicroservicesService(repo)

    create_dto = MicroserviceCreateDTO(
        service_id="s_test_get",
        name="Test Microservice Get",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    created = await service.create_microservice(create_dto.to_model())
    fetched = await service.get_microservice(created.microservice_id)
    response_dto = MicroserviceResponseDTO.from_model(fetched)

    assert response_dto.microservice_id == created.microservice_id
    assert response_dto.service_id == "s_test_get"
    assert response_dto.name == "Test Microservice Get"
    assert response_dto.resources.cpu == 2
    assert response_dto.resources.ram == "2GB"

@pytest.mark.asyncio
async def test_update_microservice(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)
    service = MicroservicesService(repo)

    create_dto = MicroserviceCreateDTO(
        service_id="s_test_update",
        name="Test Microservice Update",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    created = await service.create_microservice(create_dto.to_model())

    update_dto = MicroserviceUpdateDTO(
        name="Updated Name",
        resources=ResourcesUpdateDTO(cpu=4, ram="4GB")
    )
    updated_model = MicroserviceUpdateDTO.apply_updates(update_dto, created)

    updated = await service.update_microservice(created.microservice_id, updated_model.model_dump())
    response_dto = MicroserviceResponseDTO.from_model(updated)

    assert response_dto.name == "Updated Name"
    assert response_dto.resources.cpu == 4
    assert response_dto.resources.ram == "4GB"

@pytest.mark.asyncio
async def test_delete_microservice(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)
    service = MicroservicesService(repo)

    create_dto = MicroserviceCreateDTO(
        service_id="s_test_delete",
        name="Test Microservice Delete",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    created = await service.create_microservice(create_dto.to_model())

    result = await service.delete_microservice(created.microservice_id)
    assert "deleted" in result["detail"]

    with pytest.raises(NotFoundError):
        await service.get_microservice(created.microservice_id)

