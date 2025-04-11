import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.models import RoleModel
from cryptomesh.repositories.roles_repository import RolesRepository
from cryptomesh.services.roles_service import RolesService
from fastapi import HTTPException

@pytest.fixture
async def client_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    yield db
    await db.roles.delete_many({})

@pytest.fixture
async def roles_service(client_db):
    collection = client_db.roles
    repository = RolesRepository(collection)
    service = RolesService(repository)
    return service

@pytest.mark.asyncio
async def test_insert_role():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = RolesRepository(collection=db.roles)

    role = RoleModel(
        role_id="role_test",
        name="Test Role",
        description="Role for testing",
        permissions=["read", "write"]
    )
    created = await repo.create(role)
    assert created is not None
    assert created.role_id == "role_test"

    await db.roles.delete_many({})

@pytest.mark.asyncio
async def test_get_role_by_id():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = RolesRepository(collection=db.roles)

    role = RoleModel(
        role_id="role_get",
        name="Get Role",
        description="Role to fetch",
        permissions=["read"]
    )
    await repo.create(role)
    fetched = await repo.get_by_id("role_get")
    assert fetched is not None
    assert fetched.name == "Get Role"

    await db.roles.delete_many({})

@pytest.mark.asyncio
async def test_update_role():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = RolesRepository(collection=db.roles)

    role = RoleModel(
        role_id="role_update",
        name="Old Role",
        description="Role before update",
        permissions=["read"]
    )
    await repo.create(role)

    updates = {"name": "Updated Role", "permissions": ["read", "write"]}
    updated = await repo.update("role_update", updates)
    assert updated is not None
    assert updated.name == "Updated Role"
    assert "write" in updated.permissions

    await db.roles.delete_many({})

@pytest.mark.asyncio
async def test_delete_role():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = RolesRepository(collection=db.roles)

    role = RoleModel(
        role_id="role_delete",
        name="Role to Delete",
        description="Role for deletion test",
        permissions=["read"]
    )
    await repo.create(role)
    deleted = await repo.delete("role_delete")
    assert deleted is True

    fetched = await repo.get_by_id("role_delete")
    assert fetched is None

    await db.roles.delete_many({})

@pytest.mark.asyncio
async def test_list_roles():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = RolesRepository(collection=db.roles)

    role1 = RoleModel(
        role_id="role_list1",
        name="Role List 1",
        description="First role",
        permissions=["read"]
    )
    role2 = RoleModel(
        role_id="role_list2",
        name="Role List 2",
        description="Second role",
        permissions=["write"]
    )
    await repo.create(role1)
    await repo.create(role2)

    roles = await repo.get_all()
    role_ids = [r.role_id for r in roles]
    assert "role_list1" in role_ids
    assert "role_list2" in role_ids

    await db.roles.delete_many({})