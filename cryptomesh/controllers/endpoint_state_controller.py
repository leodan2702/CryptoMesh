from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
from cryptomesh.models import EndpointStateModel
from cryptomesh.services.endpoint_state_service import EndpointStateService
from cryptomesh.repositories.endpoint_state_repository import EndpointStateRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import CryptoMeshError, NotFoundError, ValidationError
import time as T

L = get_logger(__name__)
router = APIRouter()

def get_endpoint_state_service() -> EndpointStateService:
    collection = get_collection("endpoint_states")
    repository = EndpointStateRepository(collection)
    return EndpointStateService(repository)

@router.post(
    "/endpoint-states/",
    response_model=EndpointStateModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo estado de endpoint",
    description="Crea un nuevo registro para el estado de un endpoint en la base de datos."
)
async def create_endpoint_state(state: EndpointStateModel, svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    try:
        response = await svc.create_state(state)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT_STATE.CREATED",
        "state_id": state.state_id,
        "time": elapsed
    })
    return response

@router.get(
    "/endpoint-states/",
    response_model=List[EndpointStateModel],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Listar todos los estados de endpoint",
    description="Recupera todos los registros de estado de endpoints."
)
async def list_endpoint_states(svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    try:
        states = await svc.list_states()
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.ENDPOINT_STATE.LISTED",
        "count": len(states),
        "time": elapsed
    })
    return states

@router.get(
    "/endpoint-states/{state_id}",
    response_model=EndpointStateModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener estado de endpoint por ID",
    description="Devuelve un registro de estado de endpoint específico dado su ID."
)
async def get_endpoint_state(state_id: str, svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    try:
        state = await svc.get_state(state_id)
        if not state:
            raise NotFoundError(state_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.warning({
            "event": "API.ENDPOINT_STATE.NOT_FOUND",
            "state_id": state_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT_STATE.FETCHED",
        "state_id": state_id,
        "time": elapsed
    })
    return state

@router.put(
    "/endpoint-states/{state_id}",
    response_model=EndpointStateModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar estado de endpoint por ID",
    description="Actualiza completamente un registro de estado de endpoint existente."
)
async def update_endpoint_state(state_id: str, updated: EndpointStateModel, svc: EndpointStateService = Depends(get_endpoint_state_service)):
    update_data = updated.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    try:
        result = await svc.update_state(state_id, update_data)
        if not result:
            raise NotFoundError(state_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.error({
            "event": "API.ENDPOINT_STATE.UPDATE.FAIL",
            "state_id": state_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT_STATE.UPDATED",
        "state_id": state_id,
        "updates": update_data,
        "time": elapsed
    })
    return result

@router.delete(
    "/endpoint-states/{state_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar estado de endpoint por ID",
    description="Elimina un registro de estado de endpoint de la base de datos según su ID."
)
async def delete_endpoint_state(state_id: str, svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    try:
        await svc.delete_state(state_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT_STATE.DELETED",
        "state_id": state_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)
