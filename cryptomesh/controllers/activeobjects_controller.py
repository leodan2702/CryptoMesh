from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from cryptomesh.models import ActiveObjectModel
from cryptomesh.services.activeobjects_service import ActiveObjectsService
from cryptomesh.repositories.activeobjects_repository import ActiveObjectsRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import handle_crypto_errors
import time as T

from mictlanx import AsyncClient
from axo.storage.types import AxoStorageMetadata,AxoObjectBlob,AxoObjectBlobs
from axo.storage import AxoStorage
from axo.storage.services import MictlanXStorageService
from axo.models import MetadataX
from cryptomesh.dtos.activeobject_dto import ActiveObjectCreateDTO, ActiveObjectResponseDTO, ActiveObjectUpdateDTO
import os
from cryptomesh.utils import Utils

MICTLANX_URI =os.environ.get("MICTLANX_URI", "mictlanx://mictlanx-router-0@localhost:60666?/api_version=4&protocol=http")


def axo_storage_service():
    MICTLANX = AsyncClient(
        uri              = MICTLANX_URI,
        log_output_path  = os.environ.get("MICTLANX_LOG_PATH", "/log/cryptomesh-mictlanx.log"),
        capacity_storage = "4GB",
        client_id        = "cryptomesh",
        debug            = True,
        eviction_policy  = "LRU",
    )
    return AxoStorage(
        storage = MictlanXStorageService(client=MICTLANX)
    )


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
    axo_storage: AxoStorage = Depends(axo_storage_service)
):
    t1               = T.time()
    model            = dto.to_model()
    scheme           = model.axo_schema
    code             = model.axo_code
    ao_bucket_id     = ""
    axo_key          = dto.axo_alias
    
    
    # For now keep the dict but when we have more time we create a DTO
    # to handle this metadata
    L.debug({
        "event": "API.ACTIVE_OBJECT.CREATING",
        **dto.model_dump()
    })
    attrs = {
        "_acx_metadata": MetadataX(
            axo_is_read_only     = False,
            # This is the hack to related the source code with the attrs
            axo_key              = dto.axo_alias,
            
            axo_bucket_id        = dto.axo_bucket_id,
            axo_sink_bucket_id   = dto.axo_sink_bucket_id,
            axo_source_bucket_id = dto.axo_source_bucket_id,
            axo_alias            = dto.axo_alias,
            axo_class_name       = dto.axo_class_name,
            axo_dependencies     = dto.axo_dependencies,
            axo_endpoint_id      = dto.axo_endpoint_id,
            axo_module           = dto.axo_module,
            axo_uri              = dto.axo_uri,
            axo_version          = dto.axo_version
        ),
        "_acx_local":False,
        "_acx_remote":True
    }
    # print("HERE")
    blobs = AxoObjectBlob.from_code_and_attrs(
        bucket_id = ao_bucket_id,
        key       = axo_key,
        code      = code,
        attrs     = attrs,
    )
    res = await axo_storage.put_blobs(
        bucket_id  = ao_bucket_id,
        key        = axo_key,
        blobs      = blobs,
        class_name = dto.axo_class_name
    )

    L.debug({
        "event": "AXO_BLOB.CREATED",
        "ok":res.is_ok,
        **dto.model_dump(),
        "response_time": round(T.time() - t1, 4)
    })



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

