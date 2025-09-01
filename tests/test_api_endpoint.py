# tests/test_endpoints.py
import pytest
from cryptomesh.dtos.endpoints_dto import EndpointCreateDTO, EndpointUpdateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO

@pytest.mark.asyncio
async def test_create_endpoint(client):
    dto = EndpointCreateDTO(
        name="Test Endpoint",
        image="test_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        security_policy=SecurityPolicyDTO(
            sp_id="security_manager",
            roles=["security_manager"],
            requires_authentication=True
        ),
        policy_id="TestPolicy"
    )
    response = await client.post("/api/v1/endpoints/", json=dto.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["endpoint_id"] is not None
    assert data["name"] == dto.name
    assert data["image"] == dto.image
    assert data["resources"]["cpu"] == dto.resources.cpu
    assert data["resources"]["ram"] == dto.resources.ram
    assert data["security_policy"]["sp_id"] == dto.security_policy.sp_id

@pytest.mark.asyncio
async def test_list_endpoints(client):
    response = await client.get("/api/v1/endpoints/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_endpoint(client):
    # Primero creamos un endpoint
    dto = EndpointCreateDTO(
        name="Get Endpoint",
        image="get_image",
        resources=ResourcesDTO(cpu=1, ram="1GB"),
        security_policy=SecurityPolicyDTO(
            sp_id="security_manager",
            roles=["security_manager"],
            requires_authentication=True
        ),
        policy_id="TestPolicy"
    )
    create_res = await client.post("/api/v1/endpoints/", json=dto.model_dump())
    endpoint_id = create_res.json()["endpoint_id"]

    # Obtenemos el endpoint por ID
    get_res = await client.get(f"/api/v1/endpoints/{endpoint_id}/")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["endpoint_id"] == endpoint_id
    assert data["name"] == dto.name

@pytest.mark.asyncio
async def test_update_endpoint(client):
    # Crear endpoint
    create_dto = EndpointCreateDTO(
        name="Old Endpoint",
        image="old_image",
        resources=ResourcesDTO(cpu=2, ram="2GB"),
        security_policy=SecurityPolicyDTO(
            sp_id="security_manager",
            roles=["security_manager"],
            requires_authentication=True
        ),
        policy_id="TestPolicy"
    )
    create_res = await client.post("/api/v1/endpoints/", json=create_dto.model_dump())
    endpoint_id = create_res.json()["endpoint_id"]

    # DTO de actualización parcial
    update_dto = EndpointUpdateDTO(
        name="Updated Endpoint",
        resources=ResourcesUpdateDTO(cpu=4)
    )
    update_data = update_dto.model_dump(exclude_unset=True)  # ✅ dict listo para JSON

    # Llamada PUT a la API
    update_res = await client.put(f"/api/v1/endpoints/{endpoint_id}/", json=update_data)

    # Validación
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["name"] == update_dto.name
    assert data["resources"]["cpu"] == update_dto.resources.cpu


@pytest.mark.asyncio
async def test_delete_endpoint(client):
    # Creamos un endpoint
    create_dto = EndpointCreateDTO(
        name="To Delete",
        image="delete_image",
        resources=ResourcesDTO(cpu=1, ram="1GB"),
        security_policy=SecurityPolicyDTO(
            sp_id="security_manager",
            roles=["security_manager"],
            requires_authentication=True
        ),
        policy_id="TestPolicy"
    )
    create_res = await client.post("/api/v1/endpoints/", json=create_dto.model_dump())
    endpoint_id = create_res.json()["endpoint_id"]

    # Eliminamos
    delete_res = await client.delete(f"/api/v1/endpoints/{endpoint_id}/")
    assert delete_res.status_code == 204

    # Verificamos que ya no existe
    get_res = await client.get(f"/api/v1/endpoints/{endpoint_id}/")
    assert get_res.status_code == 404




