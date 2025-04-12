import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.models import MicroserviceModel, ResourcesModel

@pytest.mark.asyncio
async def test_create_microservice():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = MicroservicesRepository(collection=db.microservices)

    microservice = MicroserviceModel(
        microservice_id="ms_test",
        service_id="s_test",
        functions=["func1", "func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    result = await repo.create(microservice)
    assert result is not None
    assert result.microservice_id == "ms_test"
    await db.microservices.delete_many({})


@pytest.mark.asyncio
async def test_get_microservice():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = MicroservicesRepository(collection=db.microservices)

    microservice = MicroserviceModel(
        microservice_id="ms_test",
        service_id="s_test",
        functions=["func1", "func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    await repo.create(microservice)
    fetched = await repo.get_by_id("ms_test")
    assert fetched is not None
    assert fetched.service_id == "s_test"
    await db.microservices.delete_many({})


@pytest.mark.asyncio
async def test_update_microservice():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = MicroservicesRepository(collection=db.microservices)

    microservice = MicroserviceModel(
        microservice_id="ms_update",
        service_id="s_test",
        functions=["func1", "func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    await repo.create(microservice)
    updates = {"functions": ["func3", "func4"]}
    updated = await repo.update("ms_update", updates)
    assert updated is not None
    assert "func3" in updated.functions
    await db.microservices.delete_many({})


@pytest.mark.asyncio
async def test_delete_microservice():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = MicroservicesRepository(collection=db.microservices)

    microservice = MicroserviceModel(
        microservice_id="ms_delete",
        service_id="s_test",
        functions=["func1", "func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    await repo.create(microservice)
    deleted = await repo.delete("ms_delete")
    assert deleted is True
    fetched = await repo.get_by_id("ms_delete")
    assert fetched is None
    await db.microservices.delete_many({})

@pytest.mark.asyncio
async def test_list_microservices():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = MicroservicesRepository(collection=db.microservices)

    microservice1 = MicroserviceModel(
        microservice_id="ms_list1",
        service_id="s_test",
        functions=["func1"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    microservice2 = MicroserviceModel(
        microservice_id="ms_list2",
        service_id="s_test",
        functions=["func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    await repo.create(microservice1)
    await repo.create(microservice2)
    microservices = await repo.get_all()
    ids = [ms.microservice_id for ms in microservices]
    assert "ms_list1" in ids
    assert "ms_list2" in ids
    await db.microservices.delete_many({})