from fastapi import APIRouter, Depends, status, Response, HTTPException
from typing import List
from cryptomesh.models import ServiceModel
from cryptomesh.services.services_services import ServicesService
from cryptomesh.repositories.services_repository import ServicesRepository
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

router = APIRouter()
L = get_logger(__name__)

def get_services_service() -> ServicesService:
    collection = get_collection("services")
    repository = ServicesRepository(collection)
    return ServicesService(repository)

@router.post(
    "/services/",
    response_model=ServiceModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo service",
    description="Crea un nuevo service en la base de datos. El ID debe ser único."
)
async def create_service(service: ServiceModel, svc: ServicesService = Depends(get_services_service)):
    t1 = T.time()
    try:
        response = await svc.create_service(service)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SERVICE.CREATED",
        "service_id": service.service_id,
        "time": elapsed
    })
    return response

@router.get(
    "/services/",
    response_model=List[ServiceModel],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los services",
    description="Recupera todos los services almacenados en la base de datos."
)
async def list_services(svc: ServicesService = Depends(get_services_service)):
    t1 = T.time()
    try:
        services = await svc.list_services()
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.SERVICE.LISTED",
        "count": len(services),
        "time": elapsed
    })
    return services

@router.get(
    "/services/{service_id}",
    response_model=ServiceModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener un service por ID",
    description="Devuelve un service específico dado su ID único."
)
async def get_service(service_id: str, svc: ServicesService = Depends(get_services_service)):
    t1 = T.time()
    try:
        service = await svc.get_service(service_id)
        if not service:
            raise NotFoundError(service_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.warning({
            "event": "API.SERVICE.NOT_FOUND",
            "service_id": service_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SERVICE.FETCHED",
        "service_id": service_id,
        "time": elapsed
    })
    return service

@router.put(
    "/services/{service_id}",
    response_model=ServiceModel,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un service por ID",
    description="Actualiza completamente un service existente."
)
async def update_service(service_id: str, updated: ServiceModel, svc: ServicesService = Depends(get_services_service)):
    update_data = updated.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    try:
        response = await svc.update_service(service_id, update_data)
        if not response:
            raise NotFoundError(service_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.error({
            "event": "API.SERVICE.UPDATE.FAIL",
            "service_id": service_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SERVICE.UPDATED",
        "service_id": service_id,
        "updates": update_data,
        "time": elapsed
    })
    return response

@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un service por ID",
    description="Elimina un service de la base de datos según su ID."
)
async def delete_service(service_id: str, svc: ServicesService = Depends(get_services_service)):
    t1 = T.time()
    try:
        await svc.delete_service(service_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SERVICE.DELETED",
        "service_id": service_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)

