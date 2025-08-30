from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.services.microservices_services import MicroservicesService
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError,
    InvalidYAML,
    CreationError,
    UnauthorizedError,
    FunctionNotFound,
)
import time as T

from cryptomesh.dtos.microservices_dto import MicroserviceCreateDTO, MicroserviceResponseDTO, MicroserviceUpdateDTO

router = APIRouter()
L = get_logger(__name__)

def get_microservices_service() -> MicroservicesService:
    collection = get_collection("microservices")
    repository = MicroservicesRepository(collection)
    return MicroservicesService(repository)

@router.post(
    "/microservices/",
    response_model=MicroserviceResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo microservicio",
    description="Crea un nuevo microservicio en la base de datos. El ID debe ser único."
)
async def create_microservice(dto: MicroserviceCreateDTO, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    try:
        model = dto.to_model()
        created = await svc.create_microservice(model)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({    
        "event": "API.MICROSERVICE.CREATED",
        "microservice_id": created.microservice_id,
        "time": elapsed
    })
    return MicroserviceResponseDTO.from_model(created)

@router.get(
    "/microservices/",
    response_model=List[MicroserviceResponseDTO],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los microservicios",
    description="Recupera todos los microservicios almacenados en la base de datos."
)
async def list_microservices(svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    try:
        microservices = await svc.list_microservices()
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.MICROSERVICE.LISTED",
        "count": len(microservices),
        "time": elapsed
    })
    return [MicroserviceResponseDTO.from_model(ms) for ms in microservices]

@router.get(
    "/microservices/{microservice_id}/",
    response_model=MicroserviceResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener un microservicio por ID",
    description="Devuelve un microservicio específico dado su ID único."
)
async def get_microservice(microservice_id: str, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    try:
        ms = await svc.get_microservice(microservice_id)
        if not ms:
            raise NotFoundError(microservice_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.warning({
            "event": "API.MICROSERVICE.NOT_FOUND",
            "microservice_id": microservice_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.MICROSERVICE.FETCHED",
        "microservice_id": microservice_id,
        "time": elapsed
    })
    return MicroserviceResponseDTO.from_model(ms)

@router.put(
    "/microservices/{microservice_id}/",
    response_model=MicroserviceResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un microservicio por ID",
    description="Actualiza completamente un microservicio existente."
)
async def update_microservice(microservice_id: str, dto: MicroserviceUpdateDTO, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    try:
        existing = await svc.get_microservice(microservice_id)
        if not existing:
            raise NotFoundError(microservice_id)

        updated_model = MicroserviceUpdateDTO.apply_updates(dto, existing)
        updated_ms = await svc.update_microservice(microservice_id, updated_model.model_dump(by_alias=True))

    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.error({
            "event": "API.MICROSERVICE.UPDATE.FAIL",
            "microservice_id": microservice_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.MICROSERVICE.UPDATED",
        "microservice_id": microservice_id,
        "time": elapsed
    })
    return MicroserviceResponseDTO.from_model(updated_ms)

@router.delete(
    "/microservices/{microservice_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un microservicio por ID",
    description="Elimina un microservicio de la base de datos según su ID."
)
async def delete_microservice(microservice_id: str, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    try:
        await svc.delete_microservice(microservice_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.MICROSERVICE.DELETED",
        "microservice_id": microservice_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)


