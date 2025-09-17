import os
from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from cryptomesh.models import EndpointModel,SummonerParams
from cryptomesh.services.endpoints_services import EndpointsService
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError,
)
import time as T
from cryptomesh.dtos.endpoints_dto import EndpointCreateDTO, EndpointResponseDTO, EndpointUpdateDTO

L = get_logger(__name__)
router = APIRouter(prefix="/endpoints")

def get_endpoints_service() -> EndpointsService:
    collection = get_collection("endpoints")
    repository = EndpointsRepository(collection)
    sp_collection = get_collection("security_policies")
    sp_repository = SecurityPolicyRepository(sp_collection)
    security_policy_service = SecurityPolicyService(sp_repository)
    x = SummonerParams(
        ip_addr     = os.environ.get("CRYPTOMESH_SUMMONER_IP_ADDR","localhost"),
        api_version = int(os.environ.get("CRYPTOMESH_SUMMONER_API_VERSION","3")),
        port        = int(os.environ.get("CRYPTOMESH_SUMMONER_PORT","15000")),
        protocol    = os.environ.get("CRYPTOMESH_SUMMONER_PROTOCOL","http")
    )
    return EndpointsService(repository, security_policy_service, summoner_params=x)

@router.post(
    "/",
    response_model=EndpointResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo endpoint",
    description="Crea un nuevo endpoint en la base de datos."
)
async def create_endpoint(dto: EndpointCreateDTO, svc: EndpointsService = Depends(get_endpoints_service)):
    t1 = T.time()
    try:
        model = dto.to_model()
        created = await svc.create_endpoint(model)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT.CREATED",
        "endpoint_id": created.endpoint_id,
        "time": elapsed
    })
    return EndpointResponseDTO.from_model(created)

@router.get(
    "/",
    response_model=List[EndpointResponseDTO],
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
    return [EndpointResponseDTO.from_model(ep) for ep in endpoints]

@router.get(
    "/{endpoint_id}/",
    response_model=EndpointResponseDTO,
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
    return EndpointResponseDTO.from_model(endpoint)

@router.put(
    "/{endpoint_id}/",
    response_model=EndpointResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un endpoint por ID",
    description="Actualiza completamente un endpoint existente."
)
async def update_endpoint(endpoint_id: str, dto: EndpointUpdateDTO, svc: EndpointsService = Depends(get_endpoints_service)):
    t1 = T.time()
    try:
        existing = await svc.get_endpoint(endpoint_id)
        if not existing:
            raise NotFoundError(endpoint_id)

        updated_model = EndpointUpdateDTO.apply_updates(dto, existing)
        updated = await svc.update_endpoint(endpoint_id, updated_model.model_dump(by_alias=True))

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
        "time": elapsed
    })
    return EndpointResponseDTO.from_model(updated)

@router.delete(
    "/{endpoint_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un endpoint por ID",
    description="Elimina un endpoint de la base de datos según su ID."
)
async def delete_endpoint(endpoint_id: str, svc: EndpointsService = Depends(get_endpoints_service)):
    try:
        t1 = T.time()
        res = await svc.delete_endpoint(endpoint_id)
        if res.is_err:
            raise res.unwrap_err()
        elapsed = round(T.time() - t1, 4)

        L.info({
            "event": "API.ENDPOINT.DELETED",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    




@router.post(
    "/deploy",
    response_model=EndpointResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Desplegar un nuevo endpoint",
    description="Desplegar un nuevo endpoint en la infraestructura."
)
async def deploy_endpoint(
    dto:EndpointCreateDTO,
    svc: EndpointsService = Depends(get_endpoints_service)
):
    t1 = T.time()
    endpoint_id = None
    try:
        model   = dto.to_model()
        created = await svc.create_endpoint(model)
        endpoint_id = created.endpoint_id
        res     = await svc.deploy(endpoint_id=endpoint_id)
        if res.is_err:
            await svc.delete_endpoint(endpoint_id=model.endpoint_id)
            raise HTTPException(status_code=500, detail=f"Failed to deploy endpoint: {model.endpoint_id} - {res.unwrap_err()}")
    except Exception as e:
        if endpoint_id:
            res = await svc.delete_endpoint(endpoint_id=endpoint_id)
        raise HTTPException(status_code=400, detail=str(e))

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT.DEPLOYED",
        "endpoint_id": created.endpoint_id,
        "time": elapsed
    })
    return EndpointResponseDTO.from_model(created)
    # res = await Sum

@router.delete(
    "/detach/{endpoint_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un endpoint",
    description="Eliminar un endpoint de la infraestructura."
)
async def detach_endpoint(
    endpoint_id:str,
    svc: EndpointsService = Depends(get_endpoints_service)
):
    res = await svc.detach(endpoint_id=endpoint_id)
    return None