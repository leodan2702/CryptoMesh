import pytest
from cryptomesh.repositories.services_repository import ServicesRepository
from cryptomesh.models import ServiceModel

# ✅ TEST: Insertar un nuevo servicio correctamente
@pytest.mark.asyncio
async def test_insert_service(get_db):
    db = get_db
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        service_id="s_unique_create",
        security_policy="security_manager",
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    result = await repo.create(service)
    assert result is not None
    assert result.security_policy == "security_manager"

# ✅ TEST: Obtener un servicio por ID
@pytest.mark.asyncio
async def test_get_service_by_id(get_db):
    db = get_db
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        service_id="s_unique_get",
        security_policy="ml1_analyst",  # ✅ asegurado para el assert
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    await repo.create(service)
    fetched = await repo.get_by_id("s_unique_get")
    assert fetched is not None
    assert fetched.security_policy == "ml1_analyst"

# ✅ TEST: Actualizar un servicio existente
@pytest.mark.asyncio
async def test_update_service(get_db):
    db = get_db
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        service_id="s_unique_update",
        security_policy="security_manager",
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    await repo.create(service)

    new_policy = {"security_policy": "ml1_analyst"}
    updated = await repo.update("s_unique_update", new_policy)
    assert updated is not None
    assert updated.security_policy == "ml1_analyst"

# ✅ TEST: Eliminar un servicio y confirmar que ya no exista
@pytest.mark.asyncio
async def test_delete_service(get_db):
    db = get_db
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        service_id="s_unique_delete",
        security_policy="security_manager",
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    await repo.create(service)

    deleted = await repo.delete("s_unique_delete")
    assert deleted is True

    fetched = await repo.get_by_id("s_unique_delete")
    assert fetched is None

# ✅ TEST: Listar todos los servicios
@pytest.mark.asyncio
async def test_list_services(get_db):
    db = get_db
    repo = ServicesRepository(collection=db.services)

    service1 = ServiceModel(
        service_id="s_unique_list_1",
        security_policy="security_manager",
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    service2 = ServiceModel(
        service_id="s_unique_list_2",
        security_policy="ml1_analyst",
        microservices=[],
        resources={"cpu": 2, "ram": "2GB"},
        policy_id="Leo_Policy"
    )
    await repo.create(service1)
    await repo.create(service2)

    services = await repo.get_all()
    service_ids = [s.service_id for s in services]
    assert "s_unique_list_1" in service_ids
    assert "s_unique_list_2" in service_ids
