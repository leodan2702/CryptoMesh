import pytest
from fastapi import HTTPException
from cryptomesh.models import FunctionResultModel
from cryptomesh.repositories.function_result_repository import FunctionResultRepository
from cryptomesh.services.function_result_service import FunctionResultService

@pytest.mark.asyncio
async def test_create_function_result(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    result = FunctionResultModel(
        state_id="fr_unique_create",
        function_id="fn_unique_create",
        metadata={"output": "value"}
    )
    created = await service.create_result(result)
    assert created is not None
    assert created.state_id == "fr_unique_create"

@pytest.mark.asyncio
async def test_list_function_results(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    await service.create_result(FunctionResultModel(
        state_id="fr_unique_list_1",
        function_id="fn_unique_list",
        metadata={"info": "one"}
    ))
    await service.create_result(FunctionResultModel(
        state_id="fr_unique_list_2",
        function_id="fn_unique_list",
        metadata={"info": "two"}
    ))

    results = await service.list_results()
    result_ids = [r.state_id for r in results]
    assert "fr_unique_list_1" in result_ids
    assert "fr_unique_list_2" in result_ids

@pytest.mark.asyncio
async def test_get_function_result(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    await service.create_result(FunctionResultModel(
        state_id="fr_unique_get",
        function_id="fn_unique_get",
        metadata={"result": "success"}
    ))

    fetched = await service.get_result("fr_unique_get")
    assert fetched is not None
    assert fetched.metadata["result"] == "success"

@pytest.mark.asyncio
async def test_update_function_result(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    await service.create_result(FunctionResultModel(
        state_id="fr_unique_update",
        function_id="fn_unique_update",
        metadata={"status": "initial"}
    ))

    updates = {"metadata": {"status": "updated"}}
    updated = await service.update_result("fr_unique_update", updates)
    assert updated is not None
    assert updated.metadata["status"] == "updated"

@pytest.mark.asyncio
async def test_delete_function_result(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    await service.create_result(FunctionResultModel(
        state_id="fr_unique_delete",
        function_id="fn_unique_delete",
        metadata={"error": "Timeout"}
    ))

    result = await service.delete_result("fr_unique_delete")
    assert "detail" in result

    with pytest.raises(HTTPException):
        await service.get_result("fr_unique_delete")


