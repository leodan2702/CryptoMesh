import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.models import SecurityPolicyModel

@pytest.mark.asyncio
async def test_create_policy():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy = SecurityPolicyModel(
        sp_id="security_manager",         
        roles=["security_manager"],        
        requires_authentication=True
    )
    result = await repo.create(policy)
    assert result is not None
    assert result.sp_id == "security_manager"

    await db.security_policies.delete_many({})

# Test: Obtener una SecurityPolicy por su ID
@pytest.mark.asyncio
async def test_get_policy():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy = SecurityPolicyModel(
        sp_id="ml1_analyst",               
        roles=["ml1_analyst"],
        requires_authentication=True
    )
    await repo.create(policy)
    fetched = await repo.get_by_id("ml1_analyst")
    assert fetched is not None
    assert fetched.sp_id == "ml1_analyst"

    await db.security_policies.delete_many({})

# Test: Actualizar una SecurityPolicy
@pytest.mark.asyncio
async def test_update_policy():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy = SecurityPolicyModel(
        sp_id="policy_to_update",
        roles=["old_role"],
        requires_authentication=True
    )
    await repo.create(policy)

    updates = {"roles": ["new_role"]}
    updated = await repo.update("policy_to_update", updates)
    assert updated is not None
    assert updated.roles == ["new_role"]

    await db.security_policies.delete_many({})

# Test: Eliminar una SecurityPolicy
@pytest.mark.asyncio
async def test_delete_policy():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy = SecurityPolicyModel(
        sp_id="policy_to_delete",
        roles=["temp_role"],
        requires_authentication=False
    )
    await repo.create(policy)
    deleted = await repo.delete("policy_to_delete")
    assert deleted is True
    fetched = await repo.get_by_id("policy_to_delete")
    assert fetched is None

    await db.security_policies.delete_many({})

# Test: Listar todas las SecurityPolicies
@pytest.mark.asyncio
async def test_list_policies():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = SecurityPolicyRepository(collection=db.security_policies)

    policy1 = SecurityPolicyModel(
        sp_id="security_manager",
        roles=["security_manager"],
        requires_authentication=True
    )
    policy2 = SecurityPolicyModel(
        sp_id="ml1_analyst",
        roles=["ml1_analyst"],
        requires_authentication=True
    )
    await repo.create(policy1)
    await repo.create(policy2)

    policies = await repo.get_all()
    sp_ids = [p.sp_id for p in policies]
    assert "security_manager" in sp_ids
    assert "ml1_analyst" in sp_ids

    await db.security_policies.delete_many({})