import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.models import (
    FunctionModel,
    ResourcesModel,
    StorageModel
)
from cryptomesh.repositories.functions_repository import FunctionsRepository
from cryptomesh.services.functions_services import FunctionsService

@pytest.mark.asyncio
async def test_create_function():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionsRepository(collection=db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_test",
        microservice_id="ms_test",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB", 
            storage_id="st_test", 
            source_path="/local/path", 
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pendiente",
        policy_id="Leo_Policy"
    )
    created = await service.create_function(function)
    assert created is not None
    assert created.function_id == "fn_test"

    await db.functions.delete_many({})

    await db.functions.delete_many({})

@pytest.mark.asyncio
async def test_get_function_by_id():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionsRepository(collection=db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_specific",
        microservice_id="ms_test",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB", 
            storage_id="st_specific", 
            source_path="/local/path", 
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pendiente",
        policy_id="Leo_Policy"
    )
    await service.create_function(function)
    fetched = await service.get_function("fn_specific")
    assert fetched is not None
    assert fetched.function_id == "fn_specific"


@pytest.mark.asyncio
async def test_get_function():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionsRepository(collection=db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_get",
        microservice_id="ms_test",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB", 
            storage_id="st_get", 
            source_path="/local/path", 
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pendiente",
        policy_id="Leo_Policy"
    )
    await service.create_function(function)
    fetched = await service.get_function("fn_get")
    assert fetched is not None
    assert fetched.function_id == "fn_get"

    await db.functions.delete_many({})

@pytest.mark.asyncio
async def test_update_function():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionsRepository(collection=db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_update",
        microservice_id="ms_test",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB", 
            storage_id="st_update", 
            source_path="/local/path", 
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pendiente",
        policy_id="Leo_Policy"
    )
    await service.create_function(function)
    updates = {"deployment_status": "deployed", "image": "updated:image"}
    updated = await service.update_function("fn_update", updates)
    assert updated is not None
    assert updated.deployment_status == "deployed"
    assert updated.image == "updated:image"

    await db.functions.delete_many({})

@pytest.mark.asyncio
async def test_delete_function():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionsRepository(collection=db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_delete",
        microservice_id="ms_test",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB", 
            storage_id="st_delete", 
            source_path="/local/path", 
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pendiente",
        policy_id="Leo_Policy"
    )
    await service.create_function(function)
    result = await service.delete_function("fn_delete")
    assert "detail" in result

    # despues la eliminación, al intentar obtener la función se debe generar error
    with pytest.raises(Exception):
        await service.get_function("fn_delete")


    await db.functions.delete_many({})