import pytest
from cryptomesh.dtos.security_policy_dto import (
    SecurityPolicyDTO,
    SecurityPolicyResponseDTO,
    SecurityPolicyUpdateDTO
)
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.errors import NotFoundError, ValidationError

@pytest.mark.asyncio
async def test_create_policy(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)
    service = SecurityPolicyService(repo)

    create_dto = SecurityPolicyDTO(
        name="Test Policy Create",
        roles=["security_manager"],
        requires_authentication=True
    )

    created = await service.create_policy(create_dto.to_model())
    response_dto = SecurityPolicyResponseDTO.from_model(created)

    assert response_dto.sp_id == created.sp_id
    assert response_dto.name == "Test Policy Create"
    assert "security_manager" in response_dto.roles
    assert response_dto.requires_authentication is True


@pytest.mark.asyncio
async def test_get_policy(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)
    service = SecurityPolicyService(repo)

    create_dto = SecurityPolicyDTO(
        name="Test Policy Get",
        roles=["ml1_analyst"],
        requires_authentication=True
    )
    created = await service.create_policy(create_dto.to_model())

    fetched = await service.get_policy(created.sp_id)
    response_dto = SecurityPolicyResponseDTO.from_model(fetched)

    assert response_dto.sp_id == created.sp_id
    assert response_dto.name == "Test Policy Get"
    assert "ml1_analyst" in response_dto.roles


@pytest.mark.asyncio
async def test_update_policy(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)
    service = SecurityPolicyService(repo)

    create_dto = SecurityPolicyDTO(
        name="Test Policy Update",
        roles=["old_role"],
        requires_authentication=True
    )
    created = await service.create_policy(create_dto.to_model())

    update_dto = SecurityPolicyUpdateDTO(
        roles=["new_role"],
        requires_authentication=False,
        name="Updated Policy Name"
    )
    updated_model = SecurityPolicyUpdateDTO.apply_updates(update_dto, created)
    updated = await service.update_policy(created.sp_id, updated_model.__dict__)
    response_dto = SecurityPolicyResponseDTO.from_model(updated)

    assert "new_role" in response_dto.roles
    assert response_dto.requires_authentication is False
    assert response_dto.name == "Updated Policy Name"


@pytest.mark.asyncio
async def test_delete_policy(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)
    service = SecurityPolicyService(repo)

    create_dto = SecurityPolicyDTO(
        name="Test Policy Delete",
        roles=["temp_role"],
        requires_authentication=False
    )
    created = await service.create_policy(create_dto.to_model())

    result = await service.delete_policy(created.sp_id)
    assert "deleted" in result["detail"]

    with pytest.raises(NotFoundError):
        await service.get_policy(created.sp_id)


@pytest.mark.asyncio
async def test_list_policies(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)
    service = SecurityPolicyService(repo)

    policy1 = SecurityPolicyDTO(
        name="Policy List 1",
        roles=["security_manager"],
        requires_authentication=True
    )
    policy2 = SecurityPolicyDTO(
        name="Policy List 2",
        roles=["ml1_analyst"],
        requires_authentication=True
    )
    await service.create_policy(policy1.to_model())
    await service.create_policy(policy2.to_model())

    policies = await service.list_policies()
    names = [p.name for p in policies]
    assert "Policy List 1" in names
    assert "Policy List 2" in names


