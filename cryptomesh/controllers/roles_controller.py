from fastapi import APIRouter, Depends, status, Response, HTTPException
from typing import List
import time as T

from cryptomesh.services.roles_service import RolesService
from cryptomesh.repositories.roles_repository import RolesRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError
)

from cryptomesh.dtos.role_dto import (
    RoleCreateDTO,
    RoleResponseDTO,
    RoleUpdateDTO
)

router = APIRouter()
L = get_logger(__name__)

def get_roles_service() -> RolesService:
    collection = get_collection("roles")
    repository = RolesRepository(collection)
    return RolesService(repository)

@router.post(
    "/roles/",
    response_model=RoleResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo rol",
    description="Crea un nuevo rol en la base de datos."
)
async def create_role(dto: RoleCreateDTO, svc: RolesService = Depends(get_roles_service)):
    t1 = T.time()
    try:
        model = dto.to_model()
        created = await svc.create_role(model)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ROLE.CREATED",
        "role_id": created.role_id,
        "time": elapsed
    })
    return RoleResponseDTO.from_model(created)

@router.get(
    "/roles/",
    response_model=List[RoleResponseDTO],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los roles",
    description="Recupera todos los roles."
)
async def list_roles(svc: RolesService = Depends(get_roles_service)):
    t1 = T.time()
    try:
        roles = await svc.list_roles()
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.ROLE.LISTED",
        "count": len(roles),
        "time": elapsed
    })
    return [RoleResponseDTO.from_model(r) for r in roles]

@router.get(
    "/roles/{role_id}/",
    response_model=RoleResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener rol por ID",
    description="Devuelve un rol específico dado su ID."
)
async def get_role(role_id: str, svc: RolesService = Depends(get_roles_service)):
    t1 = T.time()
    try:
        role = await svc.get_role(role_id)
        if not role:
            raise NotFoundError(role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ROLE.FETCHED",
        "role_id": role_id,
        "time": elapsed
    })
    return RoleResponseDTO.from_model(role)

@router.put(
    "/roles/{role_id}/",
    response_model=RoleResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar rol por ID",
    description="Actualiza un rol existente."
)
async def update_role(role_id: str, dto: RoleUpdateDTO, svc: RolesService = Depends(get_roles_service)):
    t1 = T.time()
    try:
        existing = await svc.get_role(role_id)
        if not existing:
            raise NotFoundError(role_id)

        updated_model = RoleUpdateDTO.apply_updates(dto, existing)
        updated = await svc.update_role(role_id, updated_model.model_dump(by_alias=True))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ROLE.UPDATED",
        "role_id": role_id,
        "time": elapsed
    })
    return RoleResponseDTO.from_model(updated)

@router.delete(
    "/roles/{role_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar rol por ID",
    description="Elimina un rol de la base de datos según su ID."
)
async def delete_role(role_id: str, svc: RolesService = Depends(get_roles_service)):
    t1 = T.time()
    try:
        await svc.delete_role(role_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ROLE.DELETED",
        "role_id": role_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)



