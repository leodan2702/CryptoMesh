import pytest
from cryptomesh.dtos.role_dto import RoleCreateDTO, RoleUpdateDTO, RoleResponseDTO
from cryptomesh.models import RoleModel
from cryptomesh.repositories.roles_repository import RolesRepository
from cryptomesh.services.roles_service import RolesService
from cryptomesh.errors import NotFoundError

@pytest.mark.asyncio
async def test_create_role(get_db):
    db = get_db
    repo = RolesRepository(db.roles)
    role_svc = RolesService(repo)

    create_dto = RoleCreateDTO(
        name="Test Role",
        description="Role for testing",
        permissions=["read", "write"]
    )

    created = await role_svc.create_role(create_dto.to_model(role_id="role_test_create"))
    response_dto = RoleResponseDTO.from_model(created)

    assert response_dto.role_id == created.role_id
    assert "read" in response_dto.permissions
    assert "write" in response_dto.permissions


@pytest.mark.asyncio
async def test_get_role(get_db):
    db = get_db
    repo = RolesRepository(db.roles)
    role_svc = RolesService(repo)

    create_dto = RoleCreateDTO(
        name="Get Role",
        description="Role to fetch",
        permissions=["read"]
    )

    created = await role_svc.create_role(create_dto.to_model(role_id="role_test_get"))
    fetched = await role_svc.get_role(created.role_id)
    response_dto = RoleResponseDTO.from_model(fetched)

    assert response_dto.role_id == created.role_id
    assert response_dto.name == "Get Role"
    assert "read" in response_dto.permissions


@pytest.mark.asyncio
async def test_update_role(get_db):
    db = get_db
    repo = RolesRepository(db.roles)
    role_svc = RolesService(repo)

    create_dto = RoleCreateDTO(
        name="Old Role",
        description="Role before update",
        permissions=["read"]
    )
    created = await role_svc.create_role(create_dto.to_model(role_id="role_test_update"))

    update_dto = RoleUpdateDTO(
        name="Updated Role",
        permissions=["read", "write"]
    )
    updated_model = RoleUpdateDTO.apply_updates(update_dto, created)
    updated = await role_svc.update_role(created.role_id, updated_model.model_dump())
    response_dto = RoleResponseDTO.from_model(updated)

    assert response_dto.name == "Updated Role"
    assert "write" in response_dto.permissions


@pytest.mark.asyncio
async def test_delete_role(get_db):
    db = get_db
    repo = RolesRepository(db.roles)
    role_svc = RolesService(repo)

    create_dto = RoleCreateDTO(
        name="Role to Delete",
        description="Role for deletion test",
        permissions=["read"]
    )
    created = await role_svc.create_role(create_dto.to_model(role_id="role_test_delete"))

    result = await role_svc.delete_role(created.role_id)
    assert "deleted" in result["detail"]

    with pytest.raises(NotFoundError):
        await role_svc.get_role(created.role_id)


@pytest.mark.asyncio
async def test_list_roles(get_db):
    db = get_db
    repo = RolesRepository(db.roles)
    role_svc = RolesService(repo)

    create_dto1 = RoleCreateDTO(
        name="Role List 1",
        description="First role",
        permissions=["read"]
    )
    create_dto2 = RoleCreateDTO(
        name="Role List 2",
        description="Second role",
        permissions=["write"]
    )

    await role_svc.create_role(create_dto1.to_model(role_id="role_test_list_1"))
    await role_svc.create_role(create_dto2.to_model(role_id="role_test_list_2"))

    roles = await role_svc.list_roles()
    role_ids = [r.role_id for r in roles]

    assert "role_test_list_1" in role_ids
    assert "role_test_list_2" in role_ids
