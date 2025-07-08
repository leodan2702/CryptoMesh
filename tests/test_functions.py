import pytest
from fastapi import HTTPException
from cryptomesh.models import FunctionModel, ResourcesModel, StorageModel
from cryptomesh.repositories.functions_repository import FunctionsRepository
from cryptomesh.services.functions_services import FunctionsService

# ✅ TEST: Crear una función correctamente
@pytest.mark.asyncio
async def test_create_function(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_unique_create",
        microservice_id="ms_unique_create",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB",
            storage_id="st_unique_create",
            source_path="/local/path",
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pending",
        policy_id="Leo_Policy"
    )

    created = await service.create_function(function)
    assert created is not None
    assert created.function_id == "fn_unique_create"

# ✅ TEST: Obtener una función existente
@pytest.mark.asyncio
async def test_get_function(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_unique_get",
        microservice_id="ms_unique_get",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB",
            storage_id="st_unique_get",
            source_path="/local/path",
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pending",
        policy_id="Leo_Policy"
    )

    await service.create_function(function)
    fetched = await service.get_function("fn_unique_get")
    assert fetched is not None
    assert fetched.function_id == "fn_unique_get"

# ✅ TEST: Actualizar una función existente
@pytest.mark.asyncio
async def test_update_function(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_unique_update",
        microservice_id="ms_unique_update",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB",
            storage_id="st_unique_update",
            source_path="/local/path",
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pending",
        policy_id="Leo_Policy"
    )

    await service.create_function(function)

    updates = {
        "deployment_status": "deployed",
        "image": "updated:image"
    }

    updated = await service.update_function("fn_unique_update", updates)
    assert updated is not None
    assert updated.deployment_status == "deployed"
    assert updated.image == "updated:image"

# ✅ TEST: Eliminar una función y verificar que ya no exista
@pytest.mark.asyncio
async def test_delete_function(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    function = FunctionModel(
        function_id="fn_unique_delete",
        microservice_id="ms_unique_delete",
        image="test:image",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB",
            storage_id="st_unique_delete",
            source_path="/local/path",
            sink_path="/remote/path"
        ),
        endpoint_id="ep1",
        deployment_status="pending",
        policy_id="Leo_Policy"
    )

    await service.create_function(function)

    result = await service.delete_function("fn_unique_delete")
    assert "detail" in result

    with pytest.raises(HTTPException):
        await service.get_function("fn_unique_delete")

# ✅ TEST: Listar todas las funciones creadas
@pytest.mark.asyncio
async def test_list_functions(get_db):
    db = get_db
    repo = FunctionsRepository(db.functions)
    service = FunctionsService(repo)

    fn1 = FunctionModel(
        function_id="fn_unique_list_1",
        microservice_id="ms_list_1",
        image="img1",
        resources=ResourcesModel(cpu=1, ram="1GB"),
        storage=StorageModel(
            capacity="5GB",
            storage_id="st_list_1",
            source_path="/src1",
            sink_path="/dst1"
        ),
        endpoint_id="ep1",
        deployment_status="ready",
        policy_id="Leo_Policy"
    )

    fn2 = FunctionModel(
        function_id="fn_unique_list_2",
        microservice_id="ms_list_2",
        image="img2",
        resources=ResourcesModel(cpu=2, ram="2GB"),
        storage=StorageModel(
            capacity="10GB",
            storage_id="st_list_2",
            source_path="/src2",
            sink_path="/dst2"
        ),
        endpoint_id="ep2",
        deployment_status="ready",
        policy_id="Leo_Policy"
    )

    await service.create_function(fn1)
    await service.create_function(fn2)

    results = await service.list_functions()
    ids = [f.function_id for f in results]
    assert "fn_unique_list_1" in ids
    assert "fn_unique_list_2" in ids

