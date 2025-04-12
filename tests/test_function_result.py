import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.models import FunctionResultModel
from cryptomesh.repositories.function_result_repository import FunctionResultRepository
from cryptomesh.services.function_result_service import FunctionResultService

@pytest.mark.asyncio
async def test_create_function_result():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionResultRepository(collection=db.function_results)
    service = FunctionResultService(repo)
    
    result_obj = FunctionResultModel(
        state_id="fr_test",
        function_id="fn_test",
        metadata={"output": "value"}
    )
    created = await service.create_result(result_obj)
    assert created is not None
    assert created.state_id == "fr_test"
    
    await db.function_results.delete_many({})

@pytest.mark.asyncio
async def test_list_function_results():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionResultRepository(collection=db.function_results)
    service = FunctionResultService(repo)
    
    result1 = FunctionResultModel(
        state_id="fr_list1",
        function_id="fn_list",
        metadata={"info": "one"}
    )
    result2 = FunctionResultModel(
        state_id="fr_list2",
        function_id="fn_list",
        metadata={"info": "two"}
    )
    await service.create_result(result1)
    await service.create_result(result2)
    results = await service.list_results()
    result_ids = [r.state_id for r in results]
    assert "fr_list1" in result_ids
    assert "fr_list2" in result_ids
    
    await db.function_results.delete_many({})

@pytest.mark.asyncio
async def test_get_function_result():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionResultRepository(collection=db.function_results)
    service = FunctionResultService(repo)
    
    result_obj = FunctionResultModel(
        state_id="fr_get",
        function_id="fn_get",
        metadata={"result": "success"}
    )
    await service.create_result(result_obj)
    fetched = await service.get_result("fr_get")
    assert fetched is not None
    assert fetched.metadata["result"] == "success"
    
    await db.function_results.delete_many({})

@pytest.mark.asyncio
async def test_update_function_result():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionResultRepository(collection=db.function_results)
    service = FunctionResultService(repo)
    
    result_obj = FunctionResultModel(
        state_id="fr_update",
        function_id="fn_update",
        metadata={"status": "initial"}
    )
    await service.create_result(result_obj)
    updates = {"metadata": {"status": "updated"}}
    updated = await service.update_result("fr_update", updates)
    assert updated is not None
    assert updated.metadata["status"] == "updated"
    
    await db.function_results.delete_many({})

@pytest.mark.asyncio
async def test_delete_function_result():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionResultRepository(collection=db.function_results)
    service = FunctionResultService(repo)
    
    result_obj = FunctionResultModel(
        state_id="fr_delete",
        function_id="fn_delete",
        metadata={"error": "Timeout"}
    )
    await service.create_result(result_obj)
    res = await service.delete_result("fr_delete")
    assert "detail" in res
    
    with pytest.raises(Exception):
        await service.get_result("fr_delete")
    
    await db.function_results.delete_many({})