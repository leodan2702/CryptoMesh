import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.repositories.services_repository import ServicesRepository
from cryptomesh.models import ServiceModel


@pytest.mark.asyncio
async def test_insert_service():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        service_id="s_security",            
        security_policy="security_manager",
        microservices=[],                  
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    result = await repo.create(service)
    # Compare string sp_id
    assert result.security_policy == "security_manager"

    await db.services.delete_many({})

@pytest.mark.asyncio
async def test_get_service_by_id():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        service_id="s_ml",                
        security_policy="ml1_analyst",       
        microservices=[],                   
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    await repo.create(service)
    fetched = await repo.get_by_id("s_ml")
    assert fetched is not None
    assert fetched.security_policy == "ml1_analyst"

    await db.services.delete_many({})


@pytest.mark.asyncio
async def test_update_service():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        service_id="s_security",
        security_policy="security_manager",
        microservices=[],  # Campo obligatorio
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    await repo.create(service)

    new_policy = {"security_policy": "ml1_analyst"}
    updated = await repo.update("s_security", new_policy)
    assert updated is not None
    assert updated.security_policy == "ml1_analyst"

    await db.services.delete_many({})


@pytest.mark.asyncio
async def test_delete_service():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        service_id="service_delete",
        security_policy="security_manager",
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    await repo.create(service)

    deleted = await repo.delete("service_delete")
    assert deleted is True

    fetched = await repo.get_by_id("service_delete")
    assert fetched is None

    await db.services.delete_many({})


@pytest.mark.asyncio
async def test_list_services():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = ServicesRepository(collection=db.services)

    service1 = ServiceModel(
        service_id="s_security",
        security_policy="security_manager",
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    service2 = ServiceModel(
        service_id="s_ml",
        security_policy="ml1_analyst",
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    await repo.create(service1)
    await repo.create(service2)

    services = await repo.get_all()
    service_ids = [s.service_id for s in services]
    assert "s_security" in service_ids
    assert "s_ml" in service_ids

    await db.services.delete_many({})
