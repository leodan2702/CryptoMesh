import pytest
from fastapi import HTTPException
from cryptomesh.models import FunctionStateModel
from cryptomesh.repositories.function_state_repository import FunctionStateRepository
from cryptomesh.services.function_state_service import FunctionStateService

# ✅ TEST: Crear un nuevo estado de función
@pytest.mark.asyncio
async def test_create_function_state(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    state = FunctionStateModel(
        state_id="fs_unique_create",
        function_id="fn_unique_create",
        state="running",
        metadata={"progress": "50%"}
    )
    created = await service.create_state(state)
    assert created is not None
    assert created.state_id == "fs_unique_create"

# ✅ TEST: Listar todos los estados de función
@pytest.mark.asyncio
async def test_list_function_states(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    await service.create_state(FunctionStateModel(
        state_id="fs_unique_list_1",
        function_id="fn_unique_list",
        state="running",
        metadata={"progress": "60%"}
    ))
    await service.create_state(FunctionStateModel(
        state_id="fs_unique_list_2",
        function_id="fn_unique_list",
        state="completed",
        metadata={"result": "success"}
    ))

    states = await service.list_states()
    ids = [s.state_id for s in states]
    assert "fs_unique_list_1" in ids
    assert "fs_unique_list_2" in ids

# ✅ TEST: Obtener un estado por ID
@pytest.mark.asyncio
async def test_get_function_state(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    await service.create_state(FunctionStateModel(
        state_id="fs_unique_get",
        function_id="fn_unique_get",
        state="completed",
        metadata={"result": "success"}
    ))

    fetched = await service.get_state("fs_unique_get")
    assert fetched is not None
    assert fetched.state == "completed"

# ✅ TEST: Actualizar un estado existente
@pytest.mark.asyncio
async def test_update_function_state(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    await service.create_state(FunctionStateModel(
        state_id="fs_unique_update",
        function_id="fn_unique_update",
        state="pending",
        metadata={"info": "initial"}
    ))

    updates = {"state": "running", "metadata": {"info": "in progress"}}
    updated = await service.update_state("fs_unique_update", updates)
    assert updated is not None
    assert updated.state == "running"
    assert updated.metadata["info"] == "in progress"

# ✅ TEST: Eliminar un estado y confirmar su eliminación
@pytest.mark.asyncio
async def test_delete_function_state(get_db):
    db = get_db
    repo = FunctionStateRepository(db.function_states)
    service = FunctionStateService(repo)

    await service.create_state(FunctionStateModel(
        state_id="fs_unique_delete",
        function_id="fn_unique_delete",
        state="failed",
        metadata={"error": "Timeout"}
    ))

    result = await service.delete_state("fs_unique_delete")
    assert "detail" in result

    with pytest.raises(HTTPException):
        await service.get_state("fs_unique_delete")

