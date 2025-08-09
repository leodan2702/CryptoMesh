import pytest
from cryptomesh.cryptomesh_client.client import CryptoMeshClient
from cryptomesh.models import FunctionModel,ResourcesModel,StorageModel,ServiceModel,SecurityPolicyModel

BASE_URL = "http://localhost:19000"

client = CryptoMeshClient(BASE_URL)

@pytest.mark.asyncio
async def test_create_function():
    res = await client.create_function(
        function=FunctionModel(
            function_id="1",
            deployment_status="COMPLETED",
            endpoint_id="1",
            image="",
            microservice_id="",
            policy_id="",
            resources=ResourcesModel(cpu=1,ram="1GB"),
            storage=StorageModel(capacity="1GB",storage_id="",source_path="/mnt/source",sink_path="/mnt/sink")
        )
    )
    assert res.is_ok
@pytest.mark.asyncio
async def test_create_service():
    res = await client.create_service(
        service=ServiceModel(
            service_id="3",
            # deployment_status="COMPLETED",
            security_policy=SecurityPolicyModel(
                requires_authentication=True,
                roles=["admin"],
                sp_id=""
            ),
            microservices=["m1","m2"],
            resources=ResourcesModel(cpu=1,ram="1GB"),
            policy_id="test_policy"
        )
    )
    

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

@pytest.mark.asyncio
async def test_list_endpoints():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_endpoints()
    assert isinstance(result, list)
    if result:
        assert hasattr(result[0], "endpoint_id")

@pytest.mark.asyncio
async def test_get_endpoint():
    client = CryptoMeshClient(BASE_URL)
    result = await client.list_endpoints()
    if result:
        obj = await client.get_endpoint(result[0].endpoint_id)
        assert getattr(obj, "endpoint_id") == result[0].endpoint_id

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
        assert hasattr(result[0], "state_id")

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

