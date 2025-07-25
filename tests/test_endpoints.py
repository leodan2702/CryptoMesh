import pytest
from cryptomesh.models import EndpointModel, ResourcesModel, SecurityPolicyModel
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.services.endpoints_services import EndpointsService
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
from fastapi import HTTPException


@pytest.mark.asyncio
async def test_create_endpoint(get_db):
    db = get_db
    sp_repo = SecurityPolicyRepository(db.security_policies)
    sp_service = SecurityPolicyService(sp_repo)
    policy = SecurityPolicyModel(
         sp_id="security_manager",
         roles=["security_manager"],
         requires_authentication=True,
         policy_id="Leo_Policy"
    )
    try:
        await sp_service.create_policy(policy)
    except Exception:
        pass

    ep_repo = EndpointsRepository(db.endpoints)
    endpoints_service = EndpointsService(ep_repo, sp_service)

    # Prueba de creación
    endpoint = EndpointModel(
         endpoint_id="ep_test1",
         name="Test Endpoint",
         image="test_image",
         resources=ResourcesModel(cpu=2, ram="2GB"),
         security_policy="security_manager",
         policy_id="Leo_Policy"
    )
    created = await endpoints_service.create_endpoint(endpoint)
    assert created is not None
    assert created.endpoint_id == "ep_test1"

@pytest.mark.asyncio
async def test_get_endpoint(get_db):
    # Conexión y configuración
    db =  get_db

    sp_repo = SecurityPolicyRepository(db.security_policies)
    sp_service = SecurityPolicyService(sp_repo)
    policy = SecurityPolicyModel(
         sp_id="security_manager",
         roles=["security_manager"],
         requires_authentication=True,
         policy_id="Leo_Policy"
    )
    try:
        await sp_service.create_policy(policy)
    except Exception:
        pass

    ep_repo = EndpointsRepository(db.endpoints)
    endpoints_service = EndpointsService(ep_repo, sp_service)

    # Prueba de obtención
    endpoint = EndpointModel(
         endpoint_id="ep_get1",
         name="Get Endpoint",
         image="test_image",
         resources=ResourcesModel(cpu=2, ram="2GB"),
         security_policy="security_manager",
         policy_id="Leo_Policy"
    )
    await endpoints_service.create_endpoint(endpoint)
    fetched = await endpoints_service.get_endpoint("ep_get1")
    assert fetched is not None
    assert fetched.endpoint_id == "ep_get1"
    assert isinstance(fetched.security_policy, str)
    assert fetched.security_policy == "security_manager"


@pytest.mark.asyncio
async def test_update_endpoint(get_db):
    # Conexión y configuración
    db =  get_db

    sp_repo = SecurityPolicyRepository(db.security_policies)
    sp_service = SecurityPolicyService(sp_repo)
    policy = SecurityPolicyModel(
         sp_id="security_manager",
         roles=["security_manager"],
         requires_authentication=True,
         policy_id="Leo_Policy"
    )
    try:
        await sp_service.create_policy(policy)
    except Exception:
        pass

    ep_repo = EndpointsRepository(db.endpoints)
    endpoints_service = EndpointsService(ep_repo, sp_service)

    # Crear y luego actualizar endpoint
    endpoint = EndpointModel(
         endpoint_id="ep_update1",
         name="Old Endpoint",
         image="old_image",
         resources=ResourcesModel(cpu=2, ram="2GB"),
         security_policy="security_manager",
         policy_id="Leo_Policy"
    )
    await endpoints_service.create_endpoint(endpoint)
    updates = {"name": "Updated Endpoint", "image": "updated_image"}
    updated = await endpoints_service.update_endpoint("ep_update1", updates)
    assert updated is not None
    assert updated.name == "Updated Endpoint"
    assert updated.image == "updated_image"


@pytest.mark.asyncio
async def test_delete_endpoint(get_db):
    # Conexión y configuración
    db= get_db

    sp_repo = SecurityPolicyRepository(db.security_policies)
    sp_service = SecurityPolicyService(sp_repo)
    policy = SecurityPolicyModel(
         sp_id="security_manager",
         roles=["security_manager"],
         requires_authentication=True,
         policy_id="Leo_Policy"
    )
    try:
        await sp_service.create_policy(policy)
    except Exception:
        pass

    ep_repo = EndpointsRepository(db.endpoints)
    endpoints_service = EndpointsService(ep_repo, sp_service)

    # Crear y borrar endpoint
    endpoint = EndpointModel(
         endpoint_id="ep_delete1",
         name="To Delete Endpoint",
         image="delete_image",
         resources=ResourcesModel(cpu=2, ram="2GB"),
         security_policy="security_manager",
         policy_id="Leo_Policy"
    )
    await endpoints_service.create_endpoint(endpoint)
    result = await endpoints_service.delete_endpoint("ep_delete1")
    # Se asume que delete_endpoint devuelve un objeto o lanza una excepción
    with pytest.raises(HTTPException):
        await endpoints_service.get_endpoint("ep_delete1")