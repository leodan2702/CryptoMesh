import pytest
from cryptomesh.dtos.services_dto import (
    ServiceCreateDTO,
    ServiceResponseDTO,
    ServiceUpdateDTO
)
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO
from cryptomesh.models import ServiceModel
from cryptomesh.repositories.services_repository import ServicesRepository
from cryptomesh.services.services_services import ServicesService
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.errors import NotFoundError

@pytest.mark.asyncio
async def test_create_service(get_db):
    db = get_db
    sp_service = SecurityPolicyService(None)  # se puede mockear o usar real si quieres
    repo = ServicesRepository(db.services)
    service_svc = ServicesService(repo, sp_service)

    policy_dto = SecurityPolicyDTO(
        sp_id="security_manager",
        roles=["security_manager"],
        requires_authentication=True
    )

    create_dto = ServiceCreateDTO(
        security_policy=policy_dto,
        microservices=[],
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    created = await service_svc.create_service(create_dto.to_model(service_id="s_test_create"))
    response_dto = ServiceResponseDTO.from_model(created)

    assert response_dto.service_id == created.service_id
    assert response_dto.security_policy.sp_id == "security_manager"


@pytest.mark.asyncio
async def test_get_service(get_db):
    db = get_db
    sp_service = SecurityPolicyService(None)
    repo = ServicesRepository(db.services)
    service_svc = ServicesService(repo, sp_service)

    policy_dto = SecurityPolicyDTO(
        sp_id="ml1_analyst",
        roles=["ml1_analyst"],
        requires_authentication=True
    )

    create_dto = ServiceCreateDTO(
        security_policy=policy_dto,
        microservices=[],
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    created = await service_svc.create_service(create_dto.to_model(service_id="s_test_get"))
    fetched = await service_svc.get_service(created.service_id)
    response_dto = ServiceResponseDTO.from_model(fetched)

    assert response_dto.service_id == created.service_id
    assert response_dto.security_policy.sp_id == "ml1_analyst"


@pytest.mark.asyncio
async def test_update_service(get_db):
    db = get_db
    sp_service = SecurityPolicyService(None)
    repo = ServicesRepository(db.services)
    service_svc = ServicesService(repo, sp_service)

    policy_dto = SecurityPolicyDTO(
        sp_id="security_manager",
        roles=["security_manager"],
        requires_authentication=True
    )

    create_dto = ServiceCreateDTO(
        security_policy=policy_dto,
        microservices=[],
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    created = await service_svc.create_service(create_dto.to_model(service_id="s_test_update"))

    update_dto = ServiceUpdateDTO(
        microservices=["ms1", "ms2"],
        resources=ResourcesUpdateDTO(cpu=4, ram="4GB")
    )

    updated_model = ServiceUpdateDTO.apply_updates(update_dto, created)
    updated = await service_svc.update_service(created.service_id, updated_model.model_dump())
    response_dto = ServiceResponseDTO.from_model(updated)

    assert "ms1" in response_dto.microservices
    assert "ms2" in response_dto.microservices
    assert response_dto.resources.cpu == 4
    assert response_dto.resources.ram == "4GB"


@pytest.mark.asyncio
async def test_delete_service(get_db):
    db = get_db
    sp_service = SecurityPolicyService(None)
    repo = ServicesRepository(db.services)
    service_svc = ServicesService(repo, sp_service)

    policy_dto = SecurityPolicyDTO(
        sp_id="security_manager",
        roles=["security_manager"],
        requires_authentication=True
    )

    create_dto = ServiceCreateDTO(
        security_policy=policy_dto,
        microservices=[],
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    created = await service_svc.create_service(create_dto.to_model(service_id="s_test_delete"))
    result = await service_svc.delete_service(created.service_id)

    assert "deleted" in result["detail"]

    with pytest.raises(NotFoundError):
        await service_svc.get_service(created.service_id)
