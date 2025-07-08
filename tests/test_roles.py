import pytest
from cryptomesh.models import RoleModel
from cryptomesh.repositories.roles_repository import RolesRepository

# ✅ TEST: Insertar un nuevo rol correctamente
@pytest.mark.asyncio
async def test_insert_role(get_db):
    db = get_db
    repo = RolesRepository(db.roles)

    role = RoleModel(
        role_id="role_test_create",
        name="Test Role",
        description="Role for testing",
        permissions=["read", "write"]
    )

    created = await repo.create(role)
    assert created is not None
    assert created.role_id == "role_test_create"
    assert created.name == "Test Role"
    assert "read" in created.permissions

# ✅ TEST: Obtener un rol por ID
@pytest.mark.asyncio
async def test_get_role_by_id(get_db):
    db = get_db
    repo = RolesRepository(db.roles)

    role = RoleModel(
        role_id="role_test_get",
        name="Get Role",
        description="Role to fetch",
        permissions=["read"]
    )

    await repo.create(role)
    fetched = await repo.get_by_id("role_test_get")
    assert fetched is not None
    assert fetched.role_id == "role_test_get"
    assert fetched.name == "Get Role"
    assert "read" in fetched.permissions

# ✅ TEST: Actualizar un rol existente
@pytest.mark.asyncio
async def test_update_role(get_db):
    db = get_db
    repo = RolesRepository(db.roles)

    role = RoleModel(
        role_id="role_test_update",
        name="Old Role",
        description="Role before update",
        permissions=["read"]
    )

    await repo.create(role)
    updates = {"name": "Updated Role", "permissions": ["read", "write"]}
    updated = await repo.update("role_test_update", updates)
    assert updated is not None
    assert updated.name == "Updated Role"
    assert "write" in updated.permissions

# ✅ TEST: Eliminar un rol y confirmar que ya no exista
@pytest.mark.asyncio
async def test_delete_role(get_db):
    db = get_db
    repo = RolesRepository(db.roles)

    role = RoleModel(
        role_id="role_test_delete",
        name="Role to Delete",
        description="Role for deletion test",
        permissions=["read"]
    )

    await repo.create(role)
    deleted = await repo.delete("role_test_delete")
    assert deleted is True

    fetched = await repo.get_by_id("role_test_delete")
    assert fetched is None

# ✅ TEST: Listar todos los roles
@pytest.mark.asyncio
async def test_list_roles(get_db):
    db = get_db
    repo = RolesRepository(db.roles)

    role1 = RoleModel(
        role_id="role_test_list_1",
        name="Role List 1",
        description="First role",
        permissions=["read"]
    )
    role2 = RoleModel(
        role_id="role_test_list_2",
        name="Role List 2",
        description="Second role",
        permissions=["write"]
    )

    await repo.create(role1)
    await repo.create(role2)

    roles = await repo.get_all()
    role_ids = [r.role_id for r in roles]
    assert "role_test_list_1" in role_ids
    assert "role_test_list_2" in role_ids
