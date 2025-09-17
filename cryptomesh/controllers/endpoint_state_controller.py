from fastapi import APIRouter, Depends, HTTPException, status, Response
from typing import List
import time as T

from cryptomesh.models import EndpointStateModel
from cryptomesh.services.endpoint_state_service import EndpointStateService
from cryptomesh.repositories.endpoint_state_repository import EndpointStateRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import handle_crypto_errors

from cryptomesh.dtos.endpoint_state_dto import (
    EndpointStateCreateDTO,
    EndpointStateResponseDTO,
    EndpointStateUpdateDTO
)

L = get_logger(__name__)
router = APIRouter()

def get_endpoint_state_service() -> EndpointStateService:
    collection = get_collection("endpoint_states")
    repository = EndpointStateRepository(collection)
    return EndpointStateService(repository)

@router.post(
    "/endpoint-states/",
    response_model=EndpointStateResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo estado de endpoint",
    description="Crea un nuevo registro para el estado de un endpoint en la base de datos."
)
@handle_crypto_errors
async def create_endpoint_state(dto: EndpointStateCreateDTO, svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    model = dto.to_model()
    created = await svc.create_state(model)

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT_STATE.CREATED",
        "state_id": created.state_id,
        "time": elapsed
    })
    return EndpointStateResponseDTO.from_model(created)

@router.get(
    "/endpoint-states/",
    response_model=List[EndpointStateResponseDTO],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los estados de endpoint",
    description="Recupera todos los registros de estado de endpoints."
)
@handle_crypto_errors
async def list_endpoint_states(svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    states = await svc.list_states()

    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.ENDPOINT_STATE.LISTED",
        "count": len(states),
        "time": elapsed
    })
    return [EndpointStateResponseDTO.from_model(s) for s in states]

@router.get(
    "/endpoint-states/{state_id}/",
    response_model=EndpointStateResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Obtener estado de endpoint por ID",
    description="Devuelve un registro de estado de endpoint específico dado su ID."
)
@handle_crypto_errors
async def get_endpoint_state(state_id: str, svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    state = await svc.get_state(state_id)

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT_STATE.FETCHED",
        "state_id": state_id,
        "time": elapsed
    })
    return EndpointStateResponseDTO.from_model(state)

@router.put(
    "/endpoint-states/{state_id}/",
    response_model=EndpointStateResponseDTO,
    status_code=status.HTTP_200_OK,
    summary="Actualizar estado de endpoint por ID",
    description="Actualiza completamente un registro de estado de endpoint existente."
)
@handle_crypto_errors
async def update_endpoint_state(state_id: str, dto: EndpointStateUpdateDTO, svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    existing = await svc.get_state(state_id)
    updated_model = EndpointStateUpdateDTO.apply_updates(dto, existing)
    updated = await svc.update_state(state_id, updated_model.model_dump(by_alias=True))

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT_STATE.UPDATED",
        "state_id": state_id,
        "time": elapsed
    })
    return EndpointStateResponseDTO.from_model(updated)

@router.delete(
    "/endpoint-states/{state_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar estado de endpoint por ID",
    description="Elimina un registro de estado de endpoint de la base de datos según su ID."
)
@handle_crypto_errors
async def delete_endpoint_state(state_id: str, svc: EndpointStateService = Depends(get_endpoint_state_service)):
    t1 = T.time()
    await svc.delete_state(state_id)

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.ENDPOINT_STATE.DELETED",
        "state_id": state_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)
