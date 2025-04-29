from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.services.microservices_services import MicroservicesService
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
import time as T

router = APIRouter()
L = get_logger(__name__)

def get_microservices_service() -> MicroservicesService:
    collection = get_collection("microservices")
    repository = MicroservicesRepository(collection)
    return MicroservicesService(repository)

@router.post(
    "/microservices/",
    response_model=MicroserviceModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo microservicio",
    description="Crea un nuevo microservicio en la base de datos. El ID debe ser único."
)
async def create_microservice(microservice: MicroserviceModel, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    response = await svc.create_microservice(microservice)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.MICROSERVICE.CREATED",
        "microservice_id": microservice.microservice_id,
        "time": elapsed
    })
    return response

@router.get(
    "/microservices/",
    response_model=List[MicroserviceModel],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los microservicios",
    description="Recupera todos los microservicios almacenados en la base de datos."
)
async def list_microservices(svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    microservices = await svc.list_microservices()
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.MICROSERVICE.LISTED",
        "count": len(microservices),
        "time": elapsed
    })
    return microservices

@router.get(
    "/microservices/{microservice_id}",
    response_model=MicroserviceModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener un microservicio por ID",
    description="Devuelve un microservicio específico dado su ID único."
)
async def get_microservice(microservice_id: str, svc: MicroservicesService = Depends(get_microservices_service)):
    t1 = T.time()
    ms = await svc.get_microservice(microservice_id)
    elapsed = round(T.time() - t1, 4)
    if not ms:
        L.warning({
            "event": "API.MICROSERVICE.NOT_FOUND",
            "microservice_id": microservice_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail="Microservicio no encontrado")
    L.info({
        "event": "API.MICROSERVICE.FETCHED",
        "microservice_id": microservice_id,
        "time": elapsed
    })
    return ms

@router.put(
    "/microservices/{microservice_id}",
    response_model=MicroserviceModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un microservicio por ID",
    description="Actualiza completamente un microservicio existente."
)
async def update_microservice(microservice_id: str, updated: MicroserviceModel, svc: MicroservicesService = Depends(get_microservices_service)):
    update_data = updated.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    updated_ms = await svc.update_microservice(microservice_id, update_data)
    elapsed = round(T.time() - t1, 4)
    if not updated_ms:
        L.error({
            "event": "API.MICROSERVICE.UPDATE.FAIL",
            "microservice_id": microservice_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail="Microservicio no encontrado o error al actualizar")
    L.info({
        "event": "API.MICROSERVICE.UPDATED",
        "microservice_id": microservice_id,
        "updates": update_data,
        "time": elapsed
    })
    return updated_ms

@router.delete(
    "/microservices/{microservice_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un microservicio por ID",
    description="Elimina un microservicio de la base de datos según su ID."
)
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


