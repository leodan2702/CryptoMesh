from fastapi import APIRouter, Depends, HTTPException
from typing import List
from cryptomesh.models import RoleModel
from cryptomesh.services.roles_service import RolesService
from cryptomesh.repositories.roles_repository import RolesRepository
from cryptomesh.db import get_collection  # Esta función debe devolver la colección "roles" de MongoDB

router = APIRouter()

def get_roles_service() -> RolesService:
    collection = get_collection("roles")
    repository = RolesRepository(collection)
    return RolesService(repository)

@router.post(
    "/roles/",
    response_model=RoleModel,
    summary="Crear un nuevo role",
    description="Crea un nuevo role en la base de datos."
)
async def create_role(role: RoleModel, service: RolesService = Depends(get_roles_service)):
    return await service.create_role(role)

@router.get(
    "/roles/",
    response_model=List[RoleModel],
    summary="Obtener todos los roles",
    description="Recupera todos los roles."
)
async def list_roles(service: RolesService = Depends(get_roles_service)):
    return await service.list_roles()

@router.get(
    "/roles/{role_id}",
    response_model=RoleModel,
    summary="Obtener role por ID",
    description="Devuelve un role específico dado su ID."
)
async def get_role(role_id: str, service: RolesService = Depends(get_roles_service)):
    return await service.get_role(role_id)

@router.put(
    "/roles/{role_id}",
    response_model=RoleModel,
    summary="Actualizar role por ID",
    description="Actualiza un role existente."
)
async def update_role(role_id: str, updated: RoleModel, service: RolesService = Depends(get_roles_service)):
    update_data = updated.dict(by_alias=True, exclude_unset=True)
    return await service.update_role(role_id, update_data)

@router.delete(
    "/roles/{role_id}",
    summary="Eliminar role por ID",
    description="Elimina un role de la base de datos según su ID."
)
async def delete_role(role_id: str, service: RolesService = Depends(get_roles_service)):
    return await service.delete_role(role_id)
