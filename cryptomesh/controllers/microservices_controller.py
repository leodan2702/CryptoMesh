from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.services.microservices_services import MicroservicesService
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import handle_crypto_errors
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
@handle_crypto_errors
async def create_microservice(dto: MicroserviceCreateDTO, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    model = dto.to_model()
    created = await svc.create_microservice(model)

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
@handle_crypto_errors
async def list_microservices(svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    microservices = await svc.list_microservices()
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
@handle_crypto_errors
async def get_microservice(microservice_id: str, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    ms = await svc.get_microservice(microservice_id)

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
@handle_crypto_errors
async def update_microservice(microservice_id: str, dto: MicroserviceUpdateDTO, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    existing = await svc.get_microservice(microservice_id)
    updated_model = MicroserviceUpdateDTO.apply_updates(dto, existing)
    updated_ms = await svc.update_microservice(microservice_id, updated_model.model_dump(by_alias=True))

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
@handle_crypto_errors
async def delete_microservice(microservice_id: str, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    await svc.delete_microservice(microservice_id)

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.MICROSERVICE.DELETED",
        "microservice_id": microservice_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)


