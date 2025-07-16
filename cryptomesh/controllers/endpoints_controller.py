from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from cryptomesh.models import EndpointModel
from cryptomesh.services.endpoints_services import EndpointsService
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import CryptoMeshError, NotFoundError, ValidationError
import time as T

L = get_logger(__name__)
router = APIRouter()

def get_endpoints_service() -> EndpointsService:
    collection = get_collection("endpoints")
    repository = EndpointsRepository(collection)
    sp_collection = get_collection("security_policies")
    sp_repository = SecurityPolicyRepository(sp_collection)
    security_policy_service = SecurityPolicyService(sp_repository)
    return EndpointsService(repository, security_policy_service)

@router.post(
    "/endpoints/",
    response_model=EndpointModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo endpoint",
    description="Crea un nuevo endpoint en la base de datos."
)
async def create_endpoint(endpoint: EndpointModel, svc: EndpointsService = Depends(get_endpoints_service)):
    t1 = T.time()
    try:
        response = await svc.create_endpoint(endpoint)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT.CREATED",
        "endpoint_id": endpoint.endpoint_id,
        "time": elapsed
    })
    return response

@router.get(
    "/endpoints/",
    response_model=List[EndpointModel],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todos los endpoints",
    description="Recupera todos los endpoints almacenados en la base de datos."
)
async def list_endpoints(svc: EndpointsService = Depends(get_endpoints_service)):
    t1 = T.time()
    try:
        endpoints = await svc.list_endpoints()
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.ENDPOINT.LISTED",
        "count": len(endpoints),
        "time": elapsed
    })
    return endpoints

@router.get(
    "/endpoints/{endpoint_id}",
    response_model=EndpointModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener un endpoint por ID",
    description="Devuelve un endpoint específico dado su ID único."
)
async def get_endpoint(endpoint_id: str, svc: EndpointsService = Depends(get_endpoints_service)):
    t1 = T.time()
    try:
        endpoint = await svc.get_endpoint(endpoint_id)
        if not endpoint:
            raise NotFoundError(endpoint_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.warning({
            "event": "API.ENDPOINT.NOT_FOUND",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT.FETCHED",
        "endpoint_id": endpoint_id,
        "time": elapsed
    })
    return endpoint

@router.put(
    "/endpoints/{endpoint_id}",
    response_model=EndpointModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un endpoint por ID",
    description="Actualiza completamente un endpoint existente."
)
async def update_endpoint(endpoint_id: str, updated: EndpointModel, svc: EndpointsService = Depends(get_endpoints_service)):
    update_data = updated.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    try:
        updated_endpoint = await svc.update_endpoint(endpoint_id, update_data)
        if not updated_endpoint:
            raise NotFoundError(endpoint_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.error({
            "event": "API.ENDPOINT.UPDATE.FAIL",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT.UPDATED",
        "endpoint_id": endpoint_id,
        "updates": update_data,
        "time": elapsed
    })
    return updated_endpoint

@router.delete(
    "/endpoints/{endpoint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un endpoint por ID",
    description="Elimina un endpoint de la base de datos según su ID."
)
async def delete_endpoint(endpoint_id: str, svc: EndpointsService = Depends(get_endpoints_service)):
    t1 = T.time()
    try:
        await svc.delete_endpoint(endpoint_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT.DELETED",
        "endpoint_id": endpoint_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)




