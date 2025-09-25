# tests/test_api_active_objects.py
import pytest
from cryptomesh.dtos.activeobject_dto import (
    ActiveObjectCreateDTO,
    ActiveObjectUpdateDTO,
)

@pytest.mark.asyncio
async def test_create_active_object(client):
    dto = ActiveObjectCreateDTO(
        axo_module="test.module",
        axo_class_name="TestClass",
        axo_version=1,
        axo_alias="Test Alias",
        axo_microservice_id="microservice-1"  # campo obligatorio agregado
    )
    response = await client.post("/api/v1/active-objects/", json=dto.model_dump())
    assert response.status_code == 201
    data = response.json()
    assert data["active_object_id"] is not None
    assert data["axo_module"] == dto.axo_module
    assert data["axo_class_name"] == dto.axo_class_name
    assert data["axo_version"] == dto.axo_version
    assert data["axo_alias"] == dto.axo_alias

@pytest.mark.asyncio
async def test_list_active_objects(client):
    response = await client.get("/api/v1/active-objects/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_active_object(client):
    # Crear primero
    dto = ActiveObjectCreateDTO(
        axo_module="get.module",
        axo_class_name="GetClass",
        axo_version=1,
        axo_microservice_id="microservice-1"  # campo obligatorio agregado
    )
    create_res = await client.post("/api/v1/active-objects/", json=dto.model_dump())
    active_object_id = create_res.json()["active_object_id"]

    # Obtener por ID
    get_res = await client.get(f"/api/v1/active-objects/{active_object_id}/")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["active_object_id"] == active_object_id
    assert data["axo_module"] == dto.axo_module

@pytest.mark.asyncio
async def test_update_active_object(client):
    # Crear primero
    create_dto = ActiveObjectCreateDTO(
        axo_module="old.module",
        axo_class_name="OldClass",
        axo_version=1,
        axo_microservice_id="microservice-1"  # campo obligatorio agregado
    )
    create_res = await client.post("/api/v1/active-objects/", json=create_dto.model_dump())
    active_object_id = create_res.json()["active_object_id"]

    # Actualizar
    update_dto = ActiveObjectUpdateDTO(
        axo_class_name="UpdatedClass",
        axo_version=2,
    )
    update_data = update_dto.model_dump(exclude_unset=True)

    update_res = await client.put(f"/api/v1/active-objects/{active_object_id}/", json=update_data)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["axo_class_name"] == update_dto.axo_class_name
    assert data["axo_version"] == update_dto.axo_version

@pytest.mark.asyncio
async def test_delete_active_object(client):
    # Crear primero
    create_dto = ActiveObjectCreateDTO(
        axo_module="delete.module",
        axo_class_name="DeleteClass",
        axo_microservice_id="microservice-1"  # campo obligatorio agregado
    )
    create_res = await client.post("/api/v1/active-objects/", json=create_dto.model_dump())
    active_object_id = create_res.json()["active_object_id"]

    # Borrar
    delete_res = await client.delete(f"/api/v1/active-objects/{active_object_id}/")
    assert delete_res.status_code == 204

    # Verificar que ya no existe
    get_res = await client.get(f"/api/v1/active-objects/{active_object_id}/")
    assert get_res.status_code == 404
