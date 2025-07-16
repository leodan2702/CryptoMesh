from fastapi import APIRouter, Depends, status, Response
from typing import List
from cryptomesh.models import RoleModel
from cryptomesh.services.roles_service import RolesService
from cryptomesh.repositories.roles_repository import RolesRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import CryptoMeshError, NotFoundError, ValidationError
import time as T

router = APIRouter()
L = get_logger(__name__)

def get_roles_service() -> RolesService:
    collection = get_collection("roles")
    repository = RolesRepository(collection)
    return RolesService(repository)

@router.post(
    "/roles/",
    response_model=RoleModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo rol",
    description="Crea un nuevo rol en la base de datos."
)
async def create_role(role: RoleModel, svc: RolesService = Depends(get_roles_service)):
    t1 = T.time()
    try:
        response = await svc.create_role(role)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ROLE.CREATED",
        "role_id": role.role_id,
        "time": elapsed
    })
    return response

@router.get(
    "/roles/",
    response_model=List[RoleModel],
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
    return roles

@router.get(
    "/roles/{role_id}",
    response_model=RoleModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener role por ID",
    description="Devuelve un role específico dado su ID."
)
async def get_role(role_id: str, svc: RolesService = Depends(get_roles_service)):
    t1 = T.time()
    try:
        role = await svc.get_role(role_id)
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
    return role

@router.put(
    "/roles/{role_id}",
    response_model=RoleModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar role por ID",
    description="Actualiza un role existente."
)
async def update_role(role_id: str, updated: RoleModel, svc: RolesService = Depends(get_roles_service)):
    update_data = updated.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    try:
        result = await svc.update_role(role_id, update_data)
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
        "updates": update_data,
        "time": elapsed
    })
    return result

@router.delete(
    "/roles/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar role por ID",
    description="Elimina un role de la base de datos según su ID."
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



