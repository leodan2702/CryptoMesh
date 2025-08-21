import pytest
from cryptomesh.dtos.function_result_dto import (
    FunctionResultCreateDTO,
    FunctionResultResponseDTO,
    FunctionResultUpdateDTO
)
from cryptomesh.models import FunctionResultModel
from cryptomesh.repositories.function_result_repository import FunctionResultRepository
from cryptomesh.services.function_result_service import FunctionResultService
from cryptomesh.errors import NotFoundError

@pytest.mark.asyncio
async def test_create_function_result(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    create_dto = FunctionResultCreateDTO(
        function_id="fn_unique_create",
        metadata={"output": "value"}
    )
    created = await service.create_result(create_dto.to_model(result_id="fr_unique_create"))
    response_dto = FunctionResultResponseDTO.from_model(created)

    assert response_dto.result_id == created.result_id
    assert response_dto.metadata["output"] == "value"


@pytest.mark.asyncio
async def test_get_function_result(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    create_dto = FunctionResultCreateDTO(
        function_id="fn_unique_get",
        metadata={"result": "success"}
    )
    created = await service.create_result(create_dto.to_model(result_id="fr_unique_get"))

    fetched = await service.get_result(created.result_id)
    response_dto = FunctionResultResponseDTO.from_model(fetched)

    assert response_dto.result_id == created.result_id
    assert response_dto.metadata["result"] == "success"


@pytest.mark.asyncio
async def test_update_function_result(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    create_dto = FunctionResultCreateDTO(
        function_id="fn_unique_update",
        metadata={"status": "initial"}
    )
    created = await service.create_result(create_dto.to_model(result_id="fr_unique_update"))

    update_dto = FunctionResultUpdateDTO(metadata={"status": "updated"})
    updated_model = FunctionResultUpdateDTO.apply_updates(update_dto, created)
    updated = await service.update_result(created.result_id, updated_model.model_dump())
    response_dto = FunctionResultResponseDTO.from_model(updated)

    assert response_dto.metadata["status"] == "updated"


@pytest.mark.asyncio
async def test_delete_function_result(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    create_dto = FunctionResultCreateDTO(
        function_id="fn_unique_delete",
        metadata={"error": "Timeout"}
    )
    created = await service.create_result(create_dto.to_model(result_id="fr_unique_delete"))

    result = await service.delete_result(created.result_id)
    assert "deleted" in result["detail"]

    with pytest.raises(NotFoundError):
        await service.get_result(created.result_id)


@pytest.mark.asyncio
async def test_list_function_results(get_db):
    db = get_db
    repo = FunctionResultRepository(db.function_results)
    service = FunctionResultService(repo)

    create_dto1 = FunctionResultCreateDTO(
        function_id="fn_list_1",
        metadata={"info": "one"}
    )
    create_dto2 = FunctionResultCreateDTO(
        function_id="fn_list_2",
        metadata={"info": "two"}
    )

    await service.create_result(create_dto1.to_model(result_id="fr_list_1"))
    await service.create_result(create_dto2.to_model(result_id="fr_list_2"))

    results = await service.list_results()
    result_ids = [r.result_id for r in results]

    assert "fr_list_1" in result_ids
    assert "fr_list_2" in result_ids


