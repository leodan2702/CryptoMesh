from fastapi import APIRouter, Depends, status, Response, HTTPException
from typing import List
import time as T

from cryptomesh.models import ServiceModel
from cryptomesh.services.services_services import ServicesService
from cryptomesh.repositories.services_repository import ServicesRepository
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
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
from cryptomesh.dtos.services_dto import ServiceCreateDTO, ServiceResponseDTO, ServiceUpdateDTO


router = APIRouter()    
L = get_logger(__name__)

def get_services_service() -> ServicesService:
    collection = get_collection("services")
    repository = ServicesRepository(collection)
    sp_collection = get_collection("security_policies")
    sp_repository = SecurityPolicyRepository(sp_collection)
    security_policy_service = SecurityPolicyService(sp_repository)
    return ServicesService(repository, security_policy_service)

@router.post(
    "/services/",
    response_model=ServiceResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo service",
    description="Crea un nuevo service en la base de datos. El ID debe ser único."
)
async def create_service(dto:ServiceCreateDTO, svc: ServicesService = Depends(get_services_service)):
    t1 = T.time()
    try:
        model = dto.to_model()
        created = await svc.create_service(model)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SERVICE.CREATED",
        "service_id": created.service_id,
        "time": elapsed
    })
    return ServiceResponseDTO.from_model(created)

@router.get(
    "/services/",
    response_model=List[ServiceResponseDTO],
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
    return [ServiceResponseDTO.from_model(s) for s in services] 

@router.get(
    "/services/{service_id}/",
    response_model=ServiceResponseDTO,
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
    return ServiceResponseDTO.from_model(service)

@router.put(
    "/services/{service_id}/",
    response_model=ServiceResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un service por ID",
    description="Actualiza completamente un service existente."
)
async def update_service(service_id: str, dto: ServiceUpdateDTO, svc: ServicesService = Depends(get_services_service)):
    t1 = T.time()
    try:
        existing = await svc.get_service(service_id)
        if not existing:
            raise NotFoundError(service_id)

        updated_model = ServiceUpdateDTO.apply_updates(dto, existing)
        updated_service = await svc.update_service(service_id, updated_model.model_dump(by_alias=True))

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
        "time": elapsed
    })
    return ServiceResponseDTO.from_model(updated_service)

@router.delete(
    "/services/{service_id}/",
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

