import pytest
from cryptomesh.dtos.endpoints_dto import EndpointCreateDTO, EndpointResponseDTO, EndpointUpdateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO, SecurityPolicyUpdateDTO
from cryptomesh.services.endpoints_services import EndpointsService
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.errors import NotFoundError

@pytest.mark.asyncio
async def test_create_endpoint(get_db):
    db = get_db
    sp_repo = SecurityPolicyRepository(db.security_policies)
    sp_service = SecurityPolicyService(sp_repo)

    # Crear política de seguridad
    policy_dto = SecurityPolicyDTO(
        sp_id="security_manager",
        roles=["security_manager"],
        requires_authentication=True
    )
    try:
        await sp_service.create_policy(policy_dto.to_model())
    except Exception:
        pass

    ep_repo = EndpointsRepository(db.endpoints)
    endpoints_service = EndpointsService(ep_repo, sp_service)

    # Crear endpoint usando DTO
    create_dto = EndpointCreateDTO(
        name="Test Endpoint",
        image="test_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        security_policy=policy_dto,
        policy_id="Leo_Policy"
    )
    created = await endpoints_service.create_endpoint(create_dto.to_model())
    response_dto = EndpointResponseDTO.from_model(created)

    assert response_dto.endpoint_id == created.endpoint_id
    assert response_dto.name == "Test Endpoint"


@pytest.mark.asyncio
async def test_get_endpoint(get_db):
    db = get_db
    sp_repo = SecurityPolicyRepository(db.security_policies)
    sp_service = SecurityPolicyService(sp_repo)
    ep_repo = EndpointsRepository(db.endpoints)
    endpoints_service = EndpointsService(ep_repo, sp_service)

    # Crear política de seguridad y endpoint
    policy_dto = SecurityPolicyDTO(
        sp_id="security_manager",
        roles=["security_manager"],
        requires_authentication=True
    )
    try:
        await sp_service.create_policy(policy_dto.to_model())
    except Exception:
        pass

    create_dto = EndpointCreateDTO(
        name="Get Endpoint",
        image="test_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        security_policy=policy_dto,
        policy_id="Leo_Policy"
    )
    created = await endpoints_service.create_endpoint(create_dto.to_model())
    fetched = await endpoints_service.get_endpoint(created.endpoint_id)
    response_dto = EndpointResponseDTO.from_model(fetched)

    assert response_dto.endpoint_id == created.endpoint_id
    assert response_dto.name == "Get Endpoint"


@pytest.mark.asyncio
async def test_update_endpoint(get_db):
    db = get_db
    sp_repo = SecurityPolicyRepository(db.security_policies)
    sp_service = SecurityPolicyService(sp_repo)
    ep_repo = EndpointsRepository(db.endpoints)
    endpoints_service = EndpointsService(ep_repo, sp_service)

    # Crear política de seguridad y endpoint
    policy_dto = SecurityPolicyDTO(
        sp_id="security_manager",
        roles=["security_manager"],
        requires_authentication=True
    )
    try:
        await sp_service.create_policy(policy_dto.to_model())
    except Exception:
        pass

    create_dto = EndpointCreateDTO(
        name="Old Endpoint",
        image="old_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        security_policy=policy_dto,
        policy_id="Leo_Policy"
    )
    created = await endpoints_service.create_endpoint(create_dto.to_model())

    update_dto = EndpointUpdateDTO(
        name="Updated Endpoint",
        image="updated_image"
    )

    updated_model = await endpoints_service.update_endpoint(
        created.endpoint_id,
        update_dto.model_dump(exclude_unset=True)
    )
    response_dto = EndpointResponseDTO.from_model(updated_model)

    assert response_dto.name == "Updated Endpoint"
    assert response_dto.image == "updated_image"


@pytest.mark.asyncio
async def test_delete_endpoint(get_db):
    db = get_db
    sp_repo = SecurityPolicyRepository(db.security_policies)
    sp_service = SecurityPolicyService(sp_repo)
    ep_repo = EndpointsRepository(db.endpoints)
    endpoints_service = EndpointsService(ep_repo, sp_service)

    # Crear política de seguridad y endpoint
    policy_dto = SecurityPolicyDTO(
        sp_id="security_manager",
        roles=["security_manager"],
        requires_authentication=True
    )
    try:
        await sp_service.create_policy(policy_dto.to_model())
    except Exception:
        pass

    create_dto = EndpointCreateDTO(
        name="To Delete Endpoint",
        image="delete_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        security_policy=policy_dto,
        policy_id="Leo_Policy"
    )
    created = await endpoints_service.create_endpoint(create_dto.to_model())

    await endpoints_service.delete_endpoint(created.endpoint_id)

    # Verificar que al buscar el endpoint eliminado se lance NotFoundError
    with pytest.raises(NotFoundError):
        await endpoints_service.get_endpoint(created.endpoint_id)

