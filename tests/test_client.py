import pytest
from cryptomesh.cryptomesh_client.client import CryptoMeshClient
from cryptomesh.models import FunctionModel,ResourcesModel,StorageModel
from cryptomesh.dtos.endpoints_dto import EndpointCreateDTO, EndpointResponseDTO,EndpointUpdateDTO
from cryptomesh.dtos.functions_dto import FunctionCreateDTO, FunctionResponseDTO, FunctionUpdateDTO
from cryptomesh.dtos.services_dto import ServiceCreateDTO, ServiceResponseDTO, ServiceUpdateDTO
from cryptomesh.dtos.microservices_dto import MicroserviceCreateDTO, MicroserviceResponseDTO, MicroserviceUpdateDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO, SecurityPolicyResponseDTO, SecurityPolicyUpdateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO,ResourcesUpdateDTO
from cryptomesh.dtos.storage_dto import StorageDTO, StorageUpdateDTO
from cryptomesh.dtos.role_dto import RoleCreateDTO, RoleResponseDTO, RoleUpdateDTO
from cryptomesh.dtos.function_state_dto import FunctionStateCreateDTO, FunctionStateResponseDTO, FunctionStateUpdateDTO
from cryptomesh.dtos.function_result_dto import FunctionResultCreateDTO, FunctionResultResponseDTO, FunctionResultUpdateDTO
from cryptomesh.dtos.endpoint_state_dto import EndpointStateCreateDTO, EndpointStateResponseDTO, EndpointStateUpdateDTO
from option import Result, Ok, Err

from cryptomesh.models import FunctionModel,ResourcesModel,StorageModel,ServiceModel,SecurityPolicyModel
BASE_URL = "http://localhost:19000"
client = CryptoMeshClient(BASE_URL)


    # ---------------------------------------------------- Function Tests ----------------------------------------------------------
@pytest.mark.asyncio
async def test_create_function():
    function=FunctionCreateDTO(
        microservice_id="m1",
        image="test_function_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        storage=StorageDTO(
            capacity="10GB",
            source_path="/src",
            sink_path="/dst"
        ),
        endpoint_id="ep-123",
        policy_id="policy-abc"
    )
    result = await client.create_function(function)
    assert result.is_ok
    function_response = result.unwrap()

    assert function_response.function_id is not None
    assert function_response.image == function.image
    assert function_response.resources.cpu == function.resources.cpu
    assert function_response.storage.capacity == function.storage.capacity
    assert function_response.storage.source_path == function.storage.source_path
    assert function_response.storage.sink_path == function.storage.sink_path
    

@pytest.mark.asyncio
async def test_get_function():
    function_create = FunctionCreateDTO(
        microservice_id="m1",
        image="test_function_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        storage=StorageDTO(
            capacity="10GB",
            source_path="/src",
            sink_path="/dst"
        ),
        endpoint_id="ep-123",
        policy_id="policy-abc"
    )
    result = await client.create_function(function_create)
    assert result.is_ok
    function_response = result.unwrap()

    function_get = await client.get_function(function_response.function_id)
    assert function_get.function_id == function_response.function_id
    assert function_get.image == function_response.image

@pytest.mark.asyncio
async def test_update_function():
    function_create = FunctionCreateDTO(
        microservice_id="m1",
        image="test_function_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        storage=StorageDTO(
            capacity="10GB",
            source_path="/src",
            sink_path="/dst"
        ),
        endpoint_id="ep-123",
        policy_id="policy-abc"
    )
    result = await client.create_function(function_create)
    assert result.is_ok
    function_response = result.unwrap()

    function_update = FunctionUpdateDTO(
        image="test_updated_image",
        resources=ResourcesUpdateDTO(cpu=1, ram="1GB"),
        storage=StorageUpdateDTO(
            capacity="5GB"
        )
    )

    update_result = await client.update_function(function_response.function_id, function_update)
    
    assert update_result.image == "test_updated_image"
    assert update_result.resources.cpu == 1
    assert update_result.resources.ram == "1GB" 
    assert update_result.storage.capacity == "5GB"

@pytest.mark.asyncio
async def test_delete_function():
    function_create = FunctionCreateDTO(
        microservice_id="m1",
        image="test_function_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        storage=StorageDTO(
            capacity="10GB",
            source_path="/src",
            sink_path="/dst"
        ),
        endpoint_id="ep-123",
        policy_id="policy-abc"
    )
    result = await client.create_function(function_create)
    assert result.is_ok
    function_response = result.unwrap()

    delete_result = await client.delete_function(function_response.function_id)
    assert result.is_ok


    # ---------------------------------------------------- Services Tests ----------------------------------------------------------
@pytest.mark.asyncio
async def test_create_service():
    client = CryptoMeshClient(BASE_URL)
    create_service = ServiceCreateDTO(
            security_policy=SecurityPolicyDTO(
                sp_id="1",
                requires_authentication=True,
                roles=["admin"],
            ),
            microservices=["m1","m2"],
            resources=ResourcesDTO(cpu=1,ram="1GB"),
            policy_id="test_policy"
        )

    result = await client.create_service(create_service)
    assert result.is_ok
    service_response = result.unwrap()
    assert service_response.service_id is not None
    assert isinstance(service_response.service_id, str)


@pytest.mark.asyncio
async def test_get_service():
    create_service = ServiceCreateDTO(
            security_policy=SecurityPolicyDTO(
                sp_id="1",
                requires_authentication=True,
                roles=["admin"],
            ),
            microservices=["m1","m2"],
            resources=ResourcesDTO(cpu=1,ram="1GB"),
            policy_id="test_policy"
    )
    service_result = await client.create_service(create_service)
    assert service_result.is_ok
    service_response = service_result.unwrap()

    endpoint = await client.get_service(service_response.service_id)
    assert endpoint.service_id == service_response.service_id
    assert endpoint.security_policy.sp_id == create_service.security_policy.sp_id

@pytest.mark.asyncio
async def test_update_service():
    create_service = ServiceCreateDTO(
        security_policy=SecurityPolicyDTO(
        sp_id="1",
            requires_authentication=True,
            roles=["admin"],
        ),
        microservices=["m1","m2"],
        resources=ResourcesDTO(cpu=1,ram="1GB"),
        policy_id="test_policy"
    )
    service_result = await client.create_service(create_service)
    assert service_result.is_ok
    service_response = service_result.unwrap()

    endpoint = await client.get_service(service_response.service_id)
    
    update_dto = ServiceUpdateDTO(
        security_policy=SecurityPolicyDTO(
            sp_id="2",
            requires_authentication=True,
            roles=["admin"],
        ),
        microservices=["m2","m3"],
        resources=ResourcesUpdateDTO(cpu=2,ram="122MB")
    )

    updated_dto = await client.update_service(service_response.service_id,update_dto)

    assert updated_dto.security_policy.sp_id == "2"


@pytest.mark.asyncio
async def test_delete_service():
    create_service = ServiceCreateDTO(
        security_policy=SecurityPolicyDTO(
        sp_id="1",
            requires_authentication=True,
            roles=["admin"],
        ),
        microservices=["m1","m2"],
        resources=ResourcesDTO(cpu=1,ram="1GB"),
        policy_id="test_policy"
    )
    service_result = await client.create_service(create_service)
    assert service_result.is_ok
    service_response = service_result.unwrap()

    delete_service = await client.delete_service(service_response.service_id)
    assert delete_service.is_ok
    assert delete_service.unwrap() is True
    

    # ---------------------------------------------------- Microervices Tests ----------------------------------------------------------

@pytest.mark.asyncio
async def test_create_microservice():
    microservice = MicroserviceCreateDTO(
        service_id="s1",
        functions=["f1","f2"],
        resources=ResourcesDTO(cpu=1,ram="1GB"),
        policy_id="test_policy"
    )

    result = await client.create_microservice(microservice)
    assert result.is_ok

    microservice_response = result.unwrap()
    assert microservice_response.service_id == "s1"


@pytest.mark.asyncio
async def test_get_microservice():
    microservice = MicroserviceCreateDTO(
        service_id="s1",
        functions=["f1","f2"],
        resources=ResourcesDTO(cpu=1,ram="1GB"),
        policy_id="test_policy"
    )

    result = await client.create_microservice(microservice)
    assert result.is_ok
    created_microservice = result.unwrap()

    microservice_get = await client.get_microservice(created_microservice.microservice_id)
    assert microservice_get.microservice_id == created_microservice.microservice_id
    assert microservice_get.service_id == "s1"

@pytest.mark.asyncio
async def test_update_microservice():
    microservice = MicroserviceCreateDTO(
        service_id="s1",
        functions=["f1","f2"],
        resources=ResourcesDTO(cpu=1,ram="1GB"),
        policy_id="test_policy"
    )

    result = await client.create_microservice(microservice)
    assert result.is_ok
    created_microservice = result.unwrap()

    update_dto = MicroserviceUpdateDTO(
        service_id="s2",
        functions=["f3","f4"],
        resources=ResourcesUpdateDTO(cpu=2,ram="2GB")
    )

    updated_dto = await client.update_microservice(created_microservice.microservice_id,update_dto)
    assert updated_dto.resources.cpu == 2
    assert updated_dto.resources.ram == "2GB"
    

@pytest.mark.asyncio
async def test_delete_microservice():
    microservice = MicroserviceCreateDTO(
        service_id="s1",
        functions=["f1","f2"],
        resources=ResourcesDTO(cpu=1,ram="1GB"),
        policy_id="test_policy"
    )

    result = await client.create_microservice(microservice)
    assert result.is_ok
    created_microservice = result.unwrap()

    deleted_microservice = await client.delete_microservice(created_microservice.microservice_id)
    assert deleted_microservice.is_ok
    assert deleted_microservice.unwrap() is True


    # ---------------------------------------------------- Endpoint Tests ----------------------------------------------------------
# ───────────────────────────────
# Test create endpoint
# ───────────────────────────────
@pytest.mark.asyncio
async def test_create_endpoint():
    policy_dto = security_policy_dto = SecurityPolicyDTO(
        sp_id="test_policy",
        roles=["admin"],
        requires_authentication=False
    )
    await client.create_security_policy(policy_dto)


    create_dto = EndpointCreateDTO(
        name="endpoint_test",
        image="test-image:latest",
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        security_policy=SecurityPolicyDTO(
            sp_id="test_policy",
            roles=["admin"],
            requires_authentication=False
        ),
        policy_id="policy-123"
    )
    result = await client.create_endpoint(create_dto)
    assert result.is_ok
    endpoint_response = result.unwrap()
    assert endpoint_response.name == "endpoint_test"


# ───────────────────────────────
# Test get endpoint
# ───────────────────────────────
@pytest.mark.asyncio
async def test_get_endpoint():
    expected_name = "endpoint-test"
    create_dto = EndpointCreateDTO(
        name=expected_name,
        image="test-image:latest",
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        security_policy=SecurityPolicyDTO(
            sp_id="test_policy",
            roles=["admin"],
            requires_authentication=False
        ),
        policy_id="policy-123"
    )    
    # Crear el endpoint
    endpoint_result = await client.create_endpoint(create_dto)
    assert endpoint_result.is_ok
    created_endpoint_response = endpoint_result.unwrap()
    
    endpoint = await client.get_endpoint(created_endpoint_response.endpoint_id)
    assert endpoint.endpoint_id == created_endpoint_response.endpoint_id
    assert endpoint.name == expected_name

# ───────────────────────────────
# Test update endpoint
# ───────────────────────────────
@pytest.mark.asyncio
async def test_update_endpoint():

    # Crear política de seguridad de prueba
    security_policy_dto = SecurityPolicyDTO(
        sp_id="test_policy",
        roles=["admin"],
        requires_authentication=False
    )
    await client.create_security_policy(security_policy_dto)

    # DTO de creación de endpoint
    create_dto = EndpointCreateDTO(
        name="endpoint-test",
        image="test-image:latest",
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        security_policy=security_policy_dto,
        policy_id="policy-123"
    )

    # Crear el endpoint
    endpoint = await client.create_endpoint(create_dto)
    assert endpoint.is_ok
    endpoint_response = endpoint.unwrap()  # EndpointResponseDTO

    # DTO de actualización: cambiar nombre, imagen y recursos
    update_dto = EndpointUpdateDTO(
        name="endpoint-updated",
        image="updated-image:latest",
        resources=ResourcesUpdateDTO(cpu=2, ram="1GB")
    )

    # Actualizar el endpoint
    updated_endpoint_dto = await client.update_endpoint(endpoint_response.endpoint_id, update_dto)

    # Validar cambios
    assert updated_endpoint_dto.endpoint_id == endpoint_response.endpoint_id
    assert updated_endpoint_dto.name == "endpoint-updated"
    assert updated_endpoint_dto.image == "updated-image:latest"
    assert updated_endpoint_dto.resources.cpu == 2
    assert updated_endpoint_dto.resources.ram == "1GB"

    # Validar que campos internos no estén expuestos
    assert not hasattr(updated_endpoint_dto, "policy_id")

# ───────────────────────────────
# Test delete endpoint
# ───────────────────────────────
@pytest.mark.asyncio
async def test_delete_endpoint():
    create_dto = EndpointCreateDTO(
        name="endpoint-to-delete",
        image="test-image:latest",
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        security_policy=SecurityPolicyDTO(
            sp_id="test_policy",
            roles=["admin"],
            requires_authentication=False
        ),
        policy_id="policy-123"
    )
    create_result = await client.create_endpoint(create_dto)
    assert create_result.is_ok
    created_endpoint_response = create_result.unwrap()

    delete_result = await client.delete_endpoint(created_endpoint_response.endpoint_id)
    assert delete_result.is_ok
    assert delete_result.unwrap() is True

 # ---------------------------------------------------- Security Policy Tests ----------------------------------------------------------
@pytest.mark.asyncio
async def test_create_security_policy():
    policy_dto = SecurityPolicyDTO(
        roles=["admin"],
        requires_authentication=False
    )
    result = await client.create_security_policy(policy_dto)
    assert result.is_ok
    security_policy_response = result.unwrap()

    assert security_policy_response.roles == ["admin"]
    assert security_policy_response.requires_authentication is False


@pytest.mark.asyncio
async def test_get_security_policy():
    create_security_policy_dto = SecurityPolicyDTO(
        roles=["admin"],
        requires_authentication=False
    )

    result = await client.create_security_policy(create_security_policy_dto)
    assert result.is_ok
    security_policy_response = result.unwrap()

    obj = await client.get_security_policy(security_policy_response.sp_id)
    assert getattr(obj, "sp_id") == security_policy_response.sp_id

@pytest.mark.asyncio
async def test_update_security_policy():
    create_security_policy_dto = SecurityPolicyDTO(
        roles=["admin"],
        requires_authentication=False
    )

    result = await client.create_security_policy(create_security_policy_dto)
    assert result.is_ok
    security_policy_response = result.unwrap()

    update_dto = SecurityPolicyUpdateDTO(
        requires_authentication=True
    )

    result_updated = await client.update_security_policy(security_policy_response.sp_id, update_dto)

    assert result_updated.requires_authentication == True

@pytest.mark.asyncio
async def test_delete_security_policy():
    create_security_policy_dto = SecurityPolicyDTO(
        roles=["admin"],
        requires_authentication=False
    )

    result = await client.create_security_policy(create_security_policy_dto)
    assert result.is_ok
    security_policy_response = result.unwrap()

    deleted = await client.delete_security_policy(security_policy_response.sp_id)
    assert deleted.is_ok
    assert deleted.unwrap() is True

 # ---------------------------------------------------- Roles Tests ----------------------------------------------------------
@pytest.mark.asyncio
async def test_create_role():
    created_role= RoleCreateDTO(
        name="test-role",
        description="Test role",
        permissions=["read", "write"]
    )

    result = await client.create_role(created_role)
    assert result.is_ok
    role_response = result.unwrap()

    assert role_response.name == "test-role"
    assert role_response.description == "Test role"
    assert role_response.permissions == ["read", "write"]


@pytest.mark.asyncio
async def test_get_role():
    create_role_dto = RoleCreateDTO(
        name="test-role",
        description="Test role",
        permissions=["read", "write"]
    )

    result = await client.create_role(create_role_dto)
    assert result.is_ok
    role_response = result.unwrap()

    obj = await client.get_role(role_response.role_id)
    assert getattr(obj, "role_id") == role_response.role_id 

@pytest.mark.asyncio
async def test_update_role():
    create_role_dto = RoleCreateDTO(
        name="test-role",
        description="Test role",
        permissions=["read", "write"]
    )

    result = await client.create_role(create_role_dto)
    assert result.is_ok
    role_response = result.unwrap()

    update_dto = RoleUpdateDTO(
        name="test-role-updated",
        description="Updated test role",
        permissions=["read", "write", "execute"]
    )

    result = await client.update_role(role_response.role_id, update_dto)
    

    assert result.name == "test-role-updated"
    assert result.description == "Updated test role"
    assert result.permissions == ["read", "write", "execute"]

@pytest.mark.asyncio
async def test_delete_role():
    create_role_dto = RoleCreateDTO(
        name="test-role",
        description="Test role",
        permissions=["read", "write"]
    )

    result = await client.create_role(create_role_dto)
    assert result.is_ok
    role_response = result.unwrap()

    deleted = await client.delete_role(role_response.role_id)
    assert deleted.is_ok
    assert deleted.unwrap() is True

 # ---------------------------------------------------- Function states Tests ----------------------------------------------------------
@pytest.mark.asyncio
async def create_function_state():
    create_dto = FunctionStateCreateDTO(
        function_id="f1",
        state="running"
    )

    result = await client.create_function_state(create_dto)
    assert result.is_ok
    function_state_response = result.unwrap()

    assert function_state_response.function_id == "f1"
    assert function_state_response.state == "running"

@pytest.mark.asyncio
async def test_get_function_state():
    create_dto = FunctionStateCreateDTO(
        function_id="f1",
        state="running"
    )

    result = await client.create_function_state(create_dto)
    assert result.is_ok
    function_state_response = result.unwrap()

    obj = await client.get_function_state(function_state_response.state_id)
    assert obj.state_id == function_state_response.state_id
    assert obj.function_id == function_state_response.function_id


@pytest.mark.asyncio
async def test_update_function_state():
    create_dto = FunctionStateCreateDTO(
        function_id="f1",
        state="running"
    )

    result = await client.create_function_state(create_dto)
    assert result.is_ok
    function_state_response = result.unwrap()

    update_dto = FunctionStateUpdateDTO(
        state="pending"
    )

    result = await client.update_function_state(function_state_response.state_id, update_dto)

    assert result.state == "pending"

@pytest.mark.asyncio
async def test_delete_function_state():
    create_dto = FunctionStateCreateDTO(
        function_id="f1",
        state="running"
    )

    result = await client.create_function_state(create_dto)
    assert result.is_ok
    function_state_response = result.unwrap()

    deleted = await client.delete_function_state(function_state_response.state_id)
    assert deleted.is_ok
    assert deleted.unwrap() is True
 # ---------------------------------------------------- Function Results Tests ----------------------------------------------------------
@pytest.mark.asyncio
async def test_create_function_result():
    create_dto = FunctionResultCreateDTO(
        function_id="f1",
        metadata={"output": "value"}
    )

    result = await client.create_function_result(create_dto)
    assert result.is_ok
    function_result_response = result.unwrap()

    assert function_result_response.function_id == "f1"
    assert function_result_response.metadata == {"output": "value"}

@pytest.mark.asyncio
async def test_get_function_result():
    create_dto = FunctionResultCreateDTO(
        function_id="f1",
        metadata={"output": "value"}
    )

    result = await client.create_function_result(create_dto)
    assert result.is_ok
    function_result_response = result.unwrap()

    obj = await client.get_function_result(function_result_response.result_id)
    assert obj.result_id == function_result_response.result_id

@pytest.mark.asyncio
async def test_update_function_result():
    create_dto = FunctionResultCreateDTO(
        function_id="f1",
        metadata={"output": "value"}
    )

    function_result_response = await client.create_function_result(create_dto)
    assert function_result_response.is_ok
    function_result_response = function_result_response.unwrap()

    update_dto = FunctionResultUpdateDTO(
        metadata={"output": "value updated"}
    )

    result = await client.update_function_result(function_result_response.result_id, update_dto)

    assert result.metadata["output"] == "value updated" 

@pytest.mark.asyncio
async def test_delete_function_result():
    create_dto = FunctionResultCreateDTO(
        function_id="f1",
        metadata={"output": "value"}
    )

    result = await client.create_function_result(create_dto)
    assert result.is_ok
    function_result_response = result.unwrap()

    deleted = await client.delete_function_result(function_result_response.result_id)
    assert deleted.is_ok
    assert deleted.unwrap() is True

 # ---------------------------------------------------- Endpoint States Tests ----------------------------------------------------------
@pytest.mark.asyncio
async def test_create_endpoint_state():
    create_dto = EndpointStateCreateDTO(
        endpoint_id="e1",
        state="running"
    )

    result = await client.create_endpoint_state(create_dto)
    assert result.is_ok
    endpoint_state_response = result.unwrap()

    assert endpoint_state_response.endpoint_id == "e1"
    assert endpoint_state_response.state == "running"

@pytest.mark.asyncio
async def test_get_endpoint_state():
    create_dto = EndpointStateCreateDTO(
        endpoint_id="e1",
        state="running"
    )

    result = await client.create_endpoint_state(create_dto)
    assert result.is_ok
    endpoint_state_response = result.unwrap()

    obj = await client.get_endpoint_state(endpoint_state_response.state_id)
    assert getattr(obj, "state_id") == endpoint_state_response.state_id

@pytest.mark.asyncio
async def test_update_endpoint_state():
    create_dto = EndpointStateCreateDTO(
        endpoint_id="e1",
        state="running"
    )

    result = await client.create_endpoint_state(create_dto)
    assert result.is_ok
    endpoint_state_response = result.unwrap()

    update_dto = EndpointStateUpdateDTO(
        state="pending"
    )

    result = await client.update_endpoint_state(endpoint_state_response.state_id, update_dto)

    assert result.state == "pending"

@pytest.mark.asyncio
async def test_delete_endpoint_state():
    create_dto = EndpointStateCreateDTO(
        endpoint_id="e1",
        state="running"
    )

    result = await client.create_endpoint_state(create_dto)
    assert result.is_ok
    endpoint_state_response = result.unwrap()

    deleted = await client.delete_endpoint_state(endpoint_state_response.state_id)
    assert deleted.is_ok
    assert deleted.unwrap() is True
