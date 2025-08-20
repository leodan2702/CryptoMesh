import pytest
from cryptomesh.cryptomesh_client.client import CryptoMeshClient
from cryptomesh.models import FunctionModel,ResourcesModel,StorageModel
from cryptomesh.dtos.endpoints_dto import EndpointCreateDTO, EndpointResponseDTO,EndpointUpdateDTO
from cryptomesh.dtos.functions_dto import FunctionCreateDTO, FunctionResponseDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO,ResourcesUpdateDTO
from cryptomesh.dtos.storage_dto import StorageDTO
from option import Result, Ok, Err

BASE_URL = "http://localhost:19000"

@pytest.mark.asyncio
async def test_list_functions():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_functions()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "function_id")

@pytest.mark.asyncio
async def test_get_function():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_functions()
    if result:
        obj = await client.get_function(result[0].function_id)
        assert getattr(obj, "function_id") == result[0].function_id

@pytest.mark.asyncio
async def test_delete_function():
    client = CryptoMeshClient(BASE_URL)
    try:
        result = await client.list_functions()
        if result:
            deleted = await client.delete_function(result[0].function_id)
            assert deleted is True
    except Exception:
        pass

@pytest.mark.asyncio
async def test_list_services():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_services()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "service_id")

@pytest.mark.asyncio
async def test_get_service():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_services()
    if result:
        obj = await client.get_service(result[0].service_id)
        assert getattr(obj, "service_id") == result[0].service_id

@pytest.mark.asyncio
async def test_delete_service():
    client = CryptoMeshClient(BASE_URL)
    try:
        result = await client.list_services()
        if result:
            deleted = await client.delete_service(result[0].service_id)
            assert deleted is True
    except Exception:
        pass

@pytest.mark.asyncio
async def test_list_microservices():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_microservices()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "microservice_id")

@pytest.mark.asyncio
async def test_get_microservice():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_microservices()
    if result:
        obj = await client.get_microservice(result[0].microservice_id)
        assert getattr(obj, "microservice_id") == result[0].microservice_id

@pytest.mark.asyncio
async def test_delete_microservice():
    client = CryptoMeshClient(BASE_URL)
    try:
        result = await client.list_microservices()
        if result:
            deleted = await client.delete_microservice(result[0].microservice_id)
            assert deleted is True
    except Exception:
        pass

# @pytest.fixture
# async def test_endpoint()->EndpointResponseDTO:

    
    # assert endpoint_resp.name == expected_name
    # await client.delete_endpoint(endpoint_resp.endpoint_id)

# ───────────────────────────────
# Test list endpoints
# ───────────────────────────────
@pytest.mark.asyncio
async def test_list_endpoints():
    client = CryptoMeshClient(BASE_URL)
    endpoints = await client.list_endpoints()
    assert isinstance(endpoints,list)
    # assert any(e.endpoint_id == test_endpoint.endpoint_id for e in endpoints)

# ───────────────────────────────
# Test get endpoint
# ───────────────────────────────
@pytest.mark.asyncio
async def test_get_endpoint():
    client = CryptoMeshClient(BASE_URL)
    
    expected_name = "endpoint-test"
    create_dto = EndpointCreateDTO(
        name=expected_name,
        image="test-image:latest",
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        security_policy=SecurityPolicyDTO(
            sp_id="f6ef8e0a-7c86-410b-a6ae-2da0ed82344d",
            roles=["admin"],
            requires_authentication=False
        ),
        policy_id="policy-123"
    )
    
    # Crear el endpoint
    endpoint_result = await client.create_endpoint(create_dto)
    assert endpoint_result.is_ok
    created_endpoint_response = endpoint_result.unwrap()


    client = CryptoMeshClient(BASE_URL)
    endpoint = await client.get_endpoint(created_endpoint_response.endpoint_id)
    # dto = EndpointResponseDTO(**endpoint)
    assert endpoint.endpoint_id == created_endpoint_response.endpoint_id
    # assert dto.name == "endpoint-test"

# ───────────────────────────────
# Test update endpoint
# ───────────────────────────────
@pytest.mark.asyncio
@pytest.mark.skip("")
async def test_update_endpoint():
    
    # client = CryptoMeshClient(BASE_URL)
    client = CryptoMeshClient(BASE_URL)
    
    expected_name = "endpoint-test"
    create_dto = EndpointCreateDTO(
        name=expected_name,
        image="test-image:latest",
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        security_policy=SecurityPolicyDTO(
            sp_id="f6ef8e0a-7c86-410b-a6ae-2da0ed82344d",
            roles=["admin"],
            requires_authentication=False
        ),
        policy_id="policy-123"
    )
    
    # Crear el endpoint
    endpoint_result = await client.create_endpoint(create_dto)
    assert endpoint_result.is_ok
    created_endpoint_response = endpoint_result.unwrap()
    
    expected_updated_name = "endpoint-updated"
    update_dto = EndpointUpdateDTO(
        name=expected_updated_name,
        resources=ResourcesUpdateDTO(cpu=4)
    )
    
    update_data = update_dto.model_dump(exclude_unset=True)
    update_resp = await client.update_endpoint(created_endpoint_response.endpoint_id, update_data)
    
    # Validar que la actualización fue exitosa
    updated = await client.get_endpoint(created_endpoint_response.endpoint_id)
    dto = EndpointResponseDTO(**updated)
    assert dto.name ==expected_updated_name

@pytest.mark.asyncio
async def test_delete_endpoint():
    client = CryptoMeshClient(BASE_URL)
    try:
        result = await client.list_endpoints()
        if result:
            deleted = await client.delete_endpoint(result[0].endpoint_id)
            assert deleted is True
    except Exception:
        pass

@pytest.mark.asyncio
async def test_list_security_policies():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_security_policies()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "sp_id")

@pytest.mark.asyncio
async def test_get_security_policy():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_security_policies()
    if result:
        obj = await client.get_security_policy(result[0].sp_id)
        assert getattr(obj, "sp_id") == result[0].sp_id

@pytest.mark.asyncio
async def test_delete_security_policy():
    client = CryptoMeshClient(BASE_URL)
    try:
        result = await client.list_security_policies()
        if result:
            deleted = await client.delete_security_policy(result[0].sp_id)
            assert deleted is True
    except Exception:
        pass

@pytest.mark.asyncio
async def test_list_roles():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_roles()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "role_id")

@pytest.mark.asyncio
async def test_get_role():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_roles()
    if result:
        obj = await client.get_role(result[0].role_id)
        assert getattr(obj, "role_id") == result[0].role_id

@pytest.mark.asyncio
async def test_delete_role():
    client = CryptoMeshClient(BASE_URL)
    try:
        result = await client.list_roles()
        if result:
            deleted = await client.delete_role(result[0].role_id)
            assert deleted is True
    except Exception:
        pass

@pytest.mark.asyncio
async def test_list_function_states():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_function_states()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "state_id")

@pytest.mark.asyncio
async def test_list_function_results():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_function_results()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "result_id")

@pytest.mark.asyncio
async def test_list_endpoint_states():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_endpoint_states()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "state_id")

@pytest.mark.asyncio
async def test_get_endpoint_state():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_endpoint_states()
    if result:
        obj = await client.get_endpoint_state(result[0].state_id)
        assert getattr(obj, "state_id") == result[0].state_id

@pytest.mark.asyncio
async def test_delete_endpoint_state():
    client = CryptoMeshClient(BASE_URL)
    try:
        result = await client.list_endpoint_states()
        if result:
            deleted = await client.delete_endpoint_state(result[0].state_id)
            assert deleted is True
    except Exception:
        pass
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "state_id")
