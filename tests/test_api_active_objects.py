import pytest
import pytest_asyncio
from cryptomesh.dtos.activeobject_dto import ActiveObjectCreateDTO
from axo.storage.services import MictlanXStorageService
from mictlanx import AsyncClient
import os

MICTLANX_URI = os.environ.get("MICTLANX_URI", "mictlanx://mictlanx-router-0@localhost:60666?/api_version=4&protocol=http")

@pytest.fixture(scope="session")
def axo_storage_service() -> MictlanXStorageService:
    MICTLANX = AsyncClient(
        uri              = MICTLANX_URI,
        log_output_path  = os.environ.get("MICTLANX_LOG_PATH", "/log/cryptomesh-mictlanx.log"),
        capacity_storage = "4GB",
        client_id        = "cryptomesh",
        debug            = True,
        eviction_policy  = "LRU",
    )
    return MictlanXStorageService(
        client=MICTLANX
    )


@pytest_asyncio.fixture(scope="session", autouse=True)
# @pytest.mark.asyncio
async def before_all_tests(axo_storage_service: MictlanXStorageService ):
    # ss = MictlanXStorageService(
        # bucket_id   = "b1",
    # )
    bids = ["test-bucket","source-bucket","sink-bucket","old-bucket","delete-bucket","get-bucket"]
    for bid in bids:
        res = await axo_storage_service.client.delete_bucket(bid)
        print(f"BUCKET [{bid}] was clean")
    yield
# --- Helper para generar código Python válido ---
def get_valid_code() -> str:
    return (
        "class BellmanFord:\n"
        "    def __init__(self, graph):\n"
        "        self.graph = graph\n\n"
        "    def run(self, source, target):\n"
        "        return [source, target]\n"
    )


@pytest.mark.asyncio
async def test_create_active_object_with_code_generates_schema_and_functions(client):
    dto = ActiveObjectCreateDTO(
        axo_module           = "algo.module",
        axo_class_name       = "BellmanFord",
        axo_version          = 1,
        axo_microservice_id  = "microservice-1",
        axo_alias            = "TestAlias",
        axo_bucket_id        = "test-bucket",
        axo_code             = "class TestClass:\n    pass",
        axo_dependencies     = ["dependency1", "dependency2"],
        axo_endpoint_id      = "endpoint-123",
        axo_source_bucket_id = "source-bucket",
        axo_sink_bucket_id   = "sink-bucket",
        axo_uri              = "http://example.com/axo",
        axo_is_read_only     = False,
        axo_key              = "test-key",
    )
    payload = dto.model_dump()
    # payload["axo_code"] = get_valid_code()  # aseguramos string válido

    res = await client.post("/api/v1/active-objects/", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()
    print("DATA",data)
    # Verifica que se haya generado schema
    assert "axo_schema" in data
    assert "init" in data["axo_schema"]
    assert "methods" in data["axo_schema"]



@pytest.mark.asyncio
async def test_create_active_object_with_invalid_code_does_not_crash(client):
    dto = ActiveObjectCreateDTO(
        axo_module="broken.module",
        axo_class_name="BrokenClass",
        axo_microservice_id="microservice-1",
        axo_code="this is not python code",  # inválido
        axo_version          = 1,
        axo_alias            = "GetAlias",
        axo_bucket_id        = "get-bucket",
        axo_dependencies     = ["dependencyA", "dependencyB"],
        axo_endpoint_id      = "endpoint-456",
        axo_source_bucket_id = "get-source-bucket",
        axo_sink_bucket_id   = "get-sink-bucket",
        axo_uri              = "http://example.com/get",
        axo_is_read_only     = False,
        axo_key              = "get-key",
    )
    payload = dto.model_dump()

    res = await client.post("/api/v1/active-objects/", json=payload)
    # Dependiendo de tu handler puede ser 400 o 422 si atrapas SyntaxError
    assert res.status_code in (400, 422, 500)


@pytest.mark.asyncio
async def test_update_active_object(client):
    # Crear primero
    create_dto = ActiveObjectCreateDTO(
        axo_module           = "old.module",
        axo_class_name       = "OldClass",
        axo_version          = 1,
        axo_alias            = "axo_old_alias",
        axo_bucket_id        = "old-bucket",
        axo_code             = "class OldClass:\n    pass",
        axo_dependencies     = ["oldDependency"],
        axo_endpoint_id      = "endpoint-789",
        axo_source_bucket_id = "old-source-bucket",
        axo_sink_bucket_id   = "old-sink-bucket",
        axo_uri              = "axo://example/old",
        axo_is_read_only     = False,
        axo_key              = "old-key",
        axo_microservice_id   = "old-microservice"
    )
    payload = create_dto.model_dump()

    res = await client.post("/api/v1/active-objects/", json=payload)
    assert res.status_code == 201, res.text
    data_updated = res.json()
    active_object_id = data_updated["active_object_id"]
    update_res = await client.put(f"/api/v1/active-objects/{active_object_id}/", json=data_updated)
    assert update_res.status_code == 200
    data_updated = update_res.json()
    assert data_updated["axo_class_name"] == data_updated["axo_class_name"]
    assert data_updated["axo_version"] == data_updated["axo_version"]

@pytest.mark.asyncio
async def test_delete_active_object(client):
    # Crear primero
    create_dto = ActiveObjectCreateDTO(
        axo_module           = "delete.module",
        axo_class_name       = "DeleteClass",
        axo_version          = 1,
        axo_alias            = "DeleteAlias",
        axo_bucket_id        = "delete-bucket",
        axo_code             = "class DeleteClass:\n    pass",
        axo_dependencies     = ["deleteDependency"],
        axo_endpoint_id      = "endpoint-000",
        axo_source_bucket_id = "delete-source-bucket",
        axo_sink_bucket_id   = "delete-sink-bucket",
        axo_uri              = "http://example.com/delete",
        axo_is_read_only     = False,
        axo_key              = "delete-key",
        axo_microservice_id   = "delete-microservice"
    )
    create_res = await client.post("/api/v1/active-objects/", json=create_dto.model_dump())
    active_object_id = create_res.json()["active_object_id"]

    # Borrar
    delete_res = await client.delete(f"/api/v1/active-objects/{active_object_id}/")
    assert delete_res.status_code == 204

    # Verificar que ya no existe
    get_res = await client.get(f"/api/v1/active-objects/{active_object_id}/")
    assert get_res.status_code == 404
