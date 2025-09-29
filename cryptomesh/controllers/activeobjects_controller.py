from typing import List
import time as T
import os
# from uuid import uuid4
# 
from fastapi import APIRouter, Depends, HTTPException, status, Response
from mictlanx import AsyncClient
from axo.storage import AxoStorage
from axo.storage.services import MictlanXStorageService
# 
from cryptomesh.services import ActiveObjectsService,StorageService
from cryptomesh.repositories.activeobjects_repository import ActiveObjectsRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import handle_crypto_errors
from cryptomesh.dtos import ActiveObjectCreateDTO, ActiveObjectResponseDTO, ActiveObjectUpdateDTO
from cryptomesh.utils import Utils
# 

MICTLANX_URI =os.environ.get("MICTLANX_URI", "mictlanx://mictlanx-router-0@localhost:60666?/api_version=4&protocol=http")

def mictlanx_storage_service() -> MictlanXStorageService:
    MICTLANX = AsyncClient(
        uri              = MICTLANX_URI,
        log_output_path  = os.environ.get("MICTLANX_LOG_PATH", "/log/cryptomesh-mictlanx.log"),
        capacity_storage = "4GB",
        client_id        = "cryptomesh",
        debug            = True,
        eviction_policy  = "LRU",
    )
    return MictlanXStorageService(
        client=MICTLANX
    )


def storage_service(mictlanx_ss: MictlanXStorageService = Depends(mictlanx_storage_service)) -> AxoStorage:
    s = AxoStorage(
        storage = mictlanx_ss
    )
    ss = StorageService(
        axo_storage= s
    )
    return ss





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
async def create_active_object(
    dto: ActiveObjectCreateDTO, 
    svc: ActiveObjectsService = Depends(get_activeobjects_service),
    storage_service: StorageService = Depends(storage_service)
):
    t1               = T.time()
    model_result   = await storage_service.put_blobs(dto = dto)
    if model_result.is_err:
        raise HTTPException(status_code=500, detail=f"Error storing active object in the storage service: {model_result.unwrap_err()}")
    model           = model_result.unwrap()
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
    t1            = T.time()
    existing      = await svc.get_active_object(active_object_id)
    updated_model = ActiveObjectUpdateDTO.apply_updates(dto, existing)
    updated_ao    = await svc.update_active_object(active_object_id, updated_model.model_dump(by_alias=True))

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

@router.get("/active-objects/{active_object_id}/schema")
async def get_oa_schema(active_object_id: str,  svc: ActiveObjectsService = Depends(get_activeobjects_service)):
    oa = await svc.get_active_object(active_object_id)
    if not oa:
        raise HTTPException(status_code=404, detail="OA not found")

    # Si ya existe el schema
    if oa.axo_schema:
        return oa.axo_schema

    if not oa.axo_code:
        raise HTTPException(status_code=400, detail="OA has no code to extract schema")

    schema = Utils.extract_schema_from_code(code = oa.axo_code)

    
    await svc.update_active_object(oa.active_object_id, {"axo_schema": schema.model_dump()})

    return schema

