import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.models import EndpointModel, ResourcesModel, SecurityPolicyModel
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.services.endpoints_services import EndpointsService
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
from fastapi import HTTPException

@pytest_asyncio.fixture
async def client_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    yield db
    await db.endpoints.delete_many({})
    await db.security_policies.delete_many({})

@pytest_asyncio.fixture
async def security_policy_service(client_db):
    sp_collection = client_db.security_policies
    sp_repository = SecurityPolicyRepository(sp_collection)
    sp_service = SecurityPolicyService(sp_repository)
    policy = SecurityPolicyModel(
         sp_id="security_manager",
         roles=["security_manager"],
         requires_authentication=True,
         policy_id="Leo_Policy"  # Aunque en SecurityPolicyModel ya no se use, aquí lo dejamos para mantener compatibilidad en tests
    )
    try:
        await sp_service.create_policy(policy)
    except Exception:
        pass
    yield sp_service

@pytest_asyncio.fixture
async def endpoints_service(client_db, security_policy_service):
    ep_collection = client_db.endpoints
    repository = EndpointsRepository(ep_collection)
    service = EndpointsService(repository, security_policy_service)
    return service

# Test: Crear un Endpoint
@pytest.mark.asyncio
async def test_create_endpoint(endpoints_service: EndpointsService):
    endpoint = EndpointModel(
         endpoint_id="ep_test",
         name="Test Endpoint",
         image="test_image",
         resources=ResourcesModel(cpu=2, ram="2GB"),
         security_policy="security_manager",
         policy_id="Leo_Policy"
    )
    created = await endpoints_service.create_endpoint(endpoint)
    assert created is not None
    assert created.endpoint_id == "ep_test"

# Test: Obtener un Endpoint (se espera que security_policy se mantenga como "security_manager")
@pytest.mark.asyncio
async def test_get_endpoint(endpoints_service: EndpointsService):
    endpoint = EndpointModel(
         endpoint_id="ep_get",
         name="Get Endpoint",
         image="test_image",
         resources=ResourcesModel(cpu=2, ram="2GB"),
         security_policy="security_manager",
         policy_id="Leo_Policy"
    )
    await endpoints_service.create_endpoint(endpoint)
    fetched = await endpoints_service.get_endpoint("ep_get")
    assert fetched is not None
    assert fetched.endpoint_id == "ep_get"
    assert isinstance(fetched.security_policy, str)
    assert fetched.security_policy == "security_manager"

# Test: Actualizar un Endpoint
@pytest.mark.asyncio
async def test_update_endpoint(endpoints_service: EndpointsService):
    endpoint = EndpointModel(
         endpoint_id="ep_update",
         name="Old Endpoint",
         image="old_image",
         resources=ResourcesModel(cpu=2, ram="2GB"),
         security_policy="security_manager",
         policy_id="Leo_Policy"
    )
    await endpoints_service.create_endpoint(endpoint)
    updates = {"name": "Updated Endpoint", "image": "updated_image"}
    updated = await endpoints_service.update_endpoint("ep_update", updates)
    assert updated is not None
    assert updated.name == "Updated Endpoint"
    assert updated.image == "updated_image"

# Test: Eliminar un Endpoint y verificar que ya no se pueda obtener
@pytest.mark.asyncio
async def test_delete_endpoint(endpoints_service: EndpointsService):
    endpoint = EndpointModel(
         endpoint_id="ep_delete",
         name="To Delete Endpoint",
         image="delete_image",
         resources=ResourcesModel(cpu=2, ram="2GB"),
         security_policy="security_manager",
         policy_id="Leo_Policy"
    )
    await endpoints_service.create_endpoint(endpoint)
    result = await endpoints_service.delete_endpoint("ep_delete")
    assert "detail" in result
    with pytest.raises(HTTPException):
        await endpoints_service.get_endpoint("ep_delete")