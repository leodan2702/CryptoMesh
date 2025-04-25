import pytest
from cryptomesh.models import MicroserviceModel, ResourcesModel
from cryptomesh.repositories.microservices_repository import MicroservicesRepository

# ✅ TEST: Crear un nuevo microservicio correctamente
@pytest.mark.asyncio
async def test_create_microservice(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)

    microservice = MicroserviceModel(
        microservice_id="ms_test_create",
        service_id="s_test_create",
        functions=["func1", "func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    result = await repo.create(microservice)
    assert result is not None
    assert result.microservice_id == "ms_test_create"
    assert result.service_id == "s_test_create"

# ✅ TEST: Obtener un microservicio por ID
@pytest.mark.asyncio
async def test_get_microservice(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)

    microservice = MicroserviceModel(
        microservice_id="ms_test_get",
        service_id="s_test_get",
        functions=["func1", "func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    await repo.create(microservice)
    fetched = await repo.get_by_id("ms_test_get")
    assert fetched is not None
    assert fetched.microservice_id == "ms_test_get"
    assert fetched.service_id == "s_test_get"

# ✅ TEST: Actualizar un microservicio existente
@pytest.mark.asyncio
async def test_update_microservice(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)

    microservice = MicroserviceModel(
        microservice_id="ms_test_update",
        service_id="s_test_update",
        functions=["func1", "func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    await repo.create(microservice)
    updates = {"functions": ["func3", "func4"]}
    updated = await repo.update("ms_test_update", updates)
    assert updated is not None
    assert updated.microservice_id == "ms_test_update"
    assert "func3" in updated.functions
    assert "func4" in updated.functions

# ✅ TEST: Eliminar un microservicio y confirmar que ya no existe
@pytest.mark.asyncio
async def test_delete_microservice(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)

    microservice = MicroserviceModel(
        microservice_id="ms_test_delete",
        service_id="s_test_delete",
        functions=["func1", "func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    await repo.create(microservice)
    deleted = await repo.delete("ms_test_delete")
    assert deleted is True

    fetched = await repo.get_by_id("ms_test_delete")
    assert fetched is None

# ✅ TEST: Listar todos los microservicios
@pytest.mark.asyncio
async def test_list_microservices(get_db):
    db = get_db
    repo = MicroservicesRepository(db.microservices)

    ms1 = MicroserviceModel(
        microservice_id="ms_test_list_1",
        service_id="s_test_list",
        functions=["func1"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )
    ms2 = MicroserviceModel(
        microservice_id="ms_test_list_2",
        service_id="s_test_list",
        functions=["func2"],
        resources=ResourcesModel(cpu=2, ram="2GB"),
        policy_id="Leo_Policy"
    )

    await repo.create(ms1)
    await repo.create(ms2)
    microservices = await repo.get_all()
    ids = [ms.microservice_id for ms in microservices]
    assert "ms_test_list_1" in ids
    assert "ms_test_list_2" in ids
