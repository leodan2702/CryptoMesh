from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from cryptomesh.models import ActiveObjectModel
from cryptomesh.services.activeobjects_service import ActiveObjectsService
from cryptomesh.repositories.activeobjects_repository import ActiveObjectsRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import handle_crypto_errors
import time as T

from cryptomesh.dtos.activeobject_dto import ActiveObjectCreateDTO, ActiveObjectResponseDTO, ActiveObjectUpdateDTO

router = APIRouter()
L = get_logger(__name__)

def get_activeobjects_service() -> ActiveObjectsService:
    collection = get_collection("active_objects")
    repository = ActiveObjectsRepository(collection)
    return ActiveObjectsService(repository)


@router.post(
    "/active-objects/",
    response_model=ActiveObjectResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo ActiveObject",
    description="Crea un nuevo ActiveObject en la base de datos. El ID debe ser único."
)
@handle_crypto_errors
async def create_active_object(dto: ActiveObjectCreateDTO, svc: ActiveObjectsService = Depends(get_activeobjects_service)):
    t1 = T.time()
    model = dto.to_model()
    created = await svc.create_active_object(model)

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ACTIVE_OBJECT.CREATED",
        "active_object_id": created.active_object_id,
        "time": elapsed
    })
    return ActiveObjectResponseDTO.from_model(created)


@router.get(
    "/active-objects/",
    response_model=List[ActiveObjectResponseDTO],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los ActiveObjects",
    description="Recupera todos los ActiveObjects almacenados en la base de datos."
)
@handle_crypto_errors
async def list_active_objects(svc: ActiveObjectsService = Depends(get_activeobjects_service)):
    t1 = T.time()
    active_objects = await svc.list_active_objects()
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.ACTIVE_OBJECT.LISTED",
        "count": len(active_objects),
        "time": elapsed
    })
    return [ActiveObjectResponseDTO.from_model(ao) for ao in active_objects]


@router.get(
    "/active-objects/{active_object_id}/",
    response_model=ActiveObjectResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener un ActiveObject por ID",
    description="Devuelve un ActiveObject específico dado su ID único."
)
@handle_crypto_errors
async def get_active_object(active_object_id: str, svc: ActiveObjectsService = Depends(get_activeobjects_service)):
    t1 = T.time()
    ao = await svc.get_active_object(active_object_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ACTIVE_OBJECT.FETCHED",
        "active_object_id": active_object_id,
        "time": elapsed
    })
    return ActiveObjectResponseDTO.from_model(ao)


@router.put(
    "/active-objects/{active_object_id}/",
    response_model=ActiveObjectResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un ActiveObject por ID",
    description="Actualiza completamente un ActiveObject existente."
)
@handle_crypto_errors
async def update_active_object(active_object_id: str, dto: ActiveObjectUpdateDTO, svc: ActiveObjectsService = Depends(get_activeobjects_service)):
    t1 = T.time()
    existing = await svc.get_active_object(active_object_id)
    updated_model = ActiveObjectUpdateDTO.apply_updates(dto, existing)
    updated_ao = await svc.update_active_object(active_object_id, updated_model.model_dump(by_alias=True))
    
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ACTIVE_OBJECT.UPDATED",
        "active_object_id": active_object_id,
        "time": elapsed
    })
    return ActiveObjectResponseDTO.from_model(updated_ao)


@router.delete(
    "/active-objects/{active_object_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un ActiveObject por ID",
    description="Elimina un ActiveObject de la base de datos según su ID."
)
@handle_crypto_errors
async def delete_active_object(active_object_id: str, svc: ActiveObjectsService = Depends(get_activeobjects_service)):
    t1 = T.time()
    await svc.delete_active_object(active_object_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ACTIVE_OBJECT.DELETED",
        "active_object_id": active_object_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)
