import pytest
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.models import SecurityPolicyModel

# ✅ TEST: Crear una nueva política de seguridad
@pytest.mark.asyncio
async def test_create_policy(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy = SecurityPolicyModel(
        sp_id="sp_test_create",
        roles=["security_manager"],
        requires_authentication=True
    )
    result = await repo.create(policy)
    assert result is not None
    assert result.sp_id == "sp_test_create"
    assert result.roles == ["security_manager"]
    assert result.requires_authentication is True

# ✅ TEST: Obtener una política por ID
@pytest.mark.asyncio
async def test_get_policy(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy = SecurityPolicyModel(
        sp_id="sp_test_get",
        roles=["ml1_analyst"],
        requires_authentication=True
    )
    await repo.create(policy)
    fetched = await repo.get_by_id("sp_test_get")
    assert fetched is not None
    assert fetched.sp_id == "sp_test_get"
    assert fetched.roles == ["ml1_analyst"]
    assert fetched.requires_authentication is True

# ✅ TEST: Actualizar una política existente
@pytest.mark.asyncio
async def test_update_policy(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy = SecurityPolicyModel(
        sp_id="sp_test_update",
        roles=["old_role"],
        requires_authentication=True
    )
    await repo.create(policy)

    updates = {"roles": ["new_role"], "requires_authentication": False}
    updated = await repo.update({"sp_id": "sp_test_update"}, updates)  # <-- filtro como dict
    assert updated is not None
    assert updated.roles == ["new_role"]
    assert updated.requires_authentication is False

# ✅ TEST: Eliminar una política y confirmar que ya no exista
@pytest.mark.asyncio
async def test_delete_policy(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy = SecurityPolicyModel(
        sp_id="sp_test_delete",
        roles=["temp_role"],
        requires_authentication=False
    )
    await repo.create(policy)
    deleted = await repo.delete({"sp_id": "sp_test_delete"})  # <-- filtro como dict
    assert deleted is True

    fetched = await repo.get_by_id("sp_test_delete")
    assert fetched is None

# ✅ TEST: Listar todas las políticas de seguridad
@pytest.mark.asyncio
async def test_list_policies(get_db):
    db = get_db
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy1 = SecurityPolicyModel(
        sp_id="sp_test_list_1",
        roles=["security_manager"],
        requires_authentication=True
    )
    policy2 = SecurityPolicyModel(
        sp_id="sp_test_list_2",
        roles=["ml1_analyst"],
        requires_authentication=True
    )
    await repo.create(policy1)
    await repo.create(policy2)

    policies = await repo.get_all()
    sp_ids = [p.sp_id for p in policies]
    assert "sp_test_list_1" in sp_ids
    assert "sp_test_list_2" in sp_ids

