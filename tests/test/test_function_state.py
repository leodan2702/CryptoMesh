import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.models import FunctionStateModel
from cryptomesh.repositories.function_state_repository import FunctionStateRepository
from cryptomesh.services.function_state_service import FunctionStateService

@pytest.mark.asyncio
async def test_create_function_state():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionStateRepository(collection=db.function_states)
    service = FunctionStateService(repo)
    
    state = FunctionStateModel(
        state_id="fs_create",
        function_id="fn_create",
        state="running",
        metadata={"progress": "50%"}
    )
    created = await service.create_state(state)
    assert created is not None
    assert created.state_id == "fs_create"
    await db.function_states.delete_many({})

    await db.function_states.delete_many({})

@pytest.mark.asyncio
async def test_list_function_states():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionStateRepository(collection=db.function_states)
    service = FunctionStateService(repo)
    
    state1 = FunctionStateModel(
        state_id="fs_list1",
        function_id="fn_list",
        state="running",
        metadata={"progress": "60%"}
    )
    state2 = FunctionStateModel(
        state_id="fs_list2",
        function_id="fn_list",
        state="completed",
        metadata={"result": "success"}
    )
    await service.create_state(state1)
    await service.create_state(state2)
    states = await service.list_states()
    state_ids = [s.state_id for s in states]
    assert "fs_list1" in state_ids
    assert "fs_list2" in state_ids

@pytest.mark.asyncio
async def test_get_function_state():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionStateRepository(collection=db.function_states)
    service = FunctionStateService(repo)
    
    state = FunctionStateModel(
        state_id="fs_get",
        function_id="fn_get",
        state="completed",
        metadata={"result": "success"}
    )
    await service.create_state(state)
    fetched = await service.get_state("fs_get")
    assert fetched is not None
    assert fetched.state == "completed"
    await db.function_states.delete_many({})

@pytest.mark.asyncio
async def test_update_function_state():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionStateRepository(collection=db.function_states)
    service = FunctionStateService(repo)
    
    state = FunctionStateModel(
        state_id="fs_update",
        function_id="fn_update",
        state="pending",
        metadata={"info": "initial"}
    )
    await service.create_state(state)
    updates = {"state": "running", "metadata": {"info": "in progress"}}
    updated = await service.update_state("fs_update", updates)
    assert updated is not None
    assert updated.state == "running"
    assert updated.metadata["info"] == "in progress"
    await db.function_states.delete_many({})

@pytest.mark.asyncio
async def test_delete_function_state():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = FunctionStateRepository(collection=db.function_states)
    service = FunctionStateService(repo)
    
    state = FunctionStateModel(
        state_id="fs_delete",
        function_id="fn_delete",
        state="failed",
        metadata={"error": "Timeout"}
    )
    await service.create_state(state)
    result = await service.delete_state("fs_delete")
    assert "detail" in result
    with pytest.raises(Exception):
        await service.get_state("fs_delete")

    await db.function_states.delete_many({})