import pytest
from cryptomesh.dtos.function_state_dto import (
    FunctionStateCreateDTO,
    FunctionStateResponseDTO,
    FunctionStateUpdateDTO
)
from cryptomesh.models import FunctionStateModel
from cryptomesh.repositories.function_state_repository import FunctionStateRepository
from cryptomesh.services.function_state_service import FunctionStateService
from cryptomesh.errors import NotFoundError

@pytest.mark.asyncio
async def test_create_function_state(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    create_dto = FunctionStateCreateDTO(
        function_id="fn_unique_create",
        state="running",
        metadata={"progress": "50%"}
    )
    created = await service.create_state(FunctionStateCreateDTO.to_model(create_dto, state_id="fs_unique_create"))
    response_dto = FunctionStateResponseDTO.from_model(created)

    assert response_dto.state_id == created.state_id
    assert response_dto.state == "running"
    assert response_dto.metadata["progress"] == "50%"


@pytest.mark.asyncio
async def test_get_function_state(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    create_dto = FunctionStateCreateDTO(
        function_id="fn_unique_get",
        state="completed",
        metadata={"result": "success"}
    )
    created = await service.create_state(FunctionStateCreateDTO.to_model(create_dto, state_id="fs_unique_get"))

    fetched = await service.get_state(created.state_id)
    response_dto = FunctionStateResponseDTO.from_model(fetched)

    assert response_dto.state_id == created.state_id
    assert response_dto.state == "completed"
    assert response_dto.metadata["result"] == "success"


@pytest.mark.asyncio
async def test_update_function_state(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    create_dto = FunctionStateCreateDTO(
        function_id="fn_unique_update",
        state="pending",
        metadata={"info": "initial"}
    )
    created = await service.create_state(FunctionStateCreateDTO.to_model(create_dto, state_id="fs_unique_update"))

    update_dto = FunctionStateUpdateDTO(
        state="running",
        metadata={"info": "in progress"}
    )
    updated_model = FunctionStateUpdateDTO.apply_updates(update_dto, created)
    updated = await service.update_state(created.state_id, updated_model.model_dump())
    response_dto = FunctionStateResponseDTO.from_model(updated)

    assert response_dto.state == "running"
    assert response_dto.metadata["info"] == "in progress"


@pytest.mark.asyncio
async def test_delete_function_state(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    create_dto = FunctionStateCreateDTO(
        function_id="fn_unique_delete",
        state="failed",
        metadata={"error": "Timeout"}
    )
    created = await service.create_state(FunctionStateCreateDTO.to_model(create_dto, state_id="fs_unique_delete"))

    result = await service.delete_state(created.state_id)
    assert "deleted" in result["detail"]

    with pytest.raises(NotFoundError):
        await service.get_state(created.state_id)


@pytest.mark.asyncio
async def test_list_function_states(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    create_dto1 = FunctionStateCreateDTO(
        function_id="fn_list_1",
        state="running",
        metadata={"progress": "60%"}
    )
    create_dto2 = FunctionStateCreateDTO(
        function_id="fn_list_2",
        state="completed",
        metadata={"result": "success"}
    )

    await service.create_state(FunctionStateCreateDTO.to_model(create_dto1, state_id="fs_list_1"))
    await service.create_state(FunctionStateCreateDTO.to_model(create_dto2, state_id="fs_list_2"))

    states = await service.list_states()
    state_ids = [s.state_id for s in states]

    assert "fs_list_1" in state_ids
    assert "fs_list_2" in state_ids
