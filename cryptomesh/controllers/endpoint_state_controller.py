from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import EndpointStateModel
from cryptomesh.services.endpoint_state_service import EndpointStateService
from cryptomesh.repositories.endpoint_state_repository import EndpointStateRepository
from cryptomesh.db import get_collection

router = APIRouter()

def get_endpoint_state_service() -> EndpointStateService:
    collection = get_collection("endpoint_states")
    repository = EndpointStateRepository(collection)
    return EndpointStateService(repository)

@router.post(
    "/endpoint-states/",
    response_model=EndpointStateModel,
    summary="Crear un nuevo estado de endpoint",
    description="Crea un nuevo registro para el estado de un endpoint en la base de datos."
)
async def create_endpoint_state(state: EndpointStateModel, service: EndpointStateService = Depends(get_endpoint_state_service)):
    return await service.create_state(state)

@router.get(
    "/endpoint-states/",
    response_model=List[EndpointStateModel],
    summary="Listar todos los estados de endpoint",
    description="Recupera todos los registros de estado de endpoints."
)
async def list_endpoint_states(service: EndpointStateService = Depends(get_endpoint_state_service)):
    return await service.list_states()

@router.get(
    "/endpoint-states/{state_id}",
    response_model=EndpointStateModel,
    summary="Obtener estado de endpoint por ID",
    description="Devuelve un registro de estado de endpoint específico dado su ID."
)
async def get_endpoint_state(state_id: str, service: EndpointStateService = Depends(get_endpoint_state_service)):
    return await service.get_state(state_id)

@router.put(
    "/endpoint-states/{state_id}",
    response_model=EndpointStateModel,
    summary="Actualizar estado de endpoint por ID",
    description="Actualiza completamente un registro de estado de endpoint existente."
)
async def update_endpoint_state(state_id: str, updated: EndpointStateModel, service: EndpointStateService = Depends(get_endpoint_state_service)):
    update_data = updated.dict(by_alias=True, exclude_unset=True)
    return await service.update_state(state_id, update_data)

@router.delete(
    "/endpoint-states/{state_id}",
    summary="Eliminar estado de endpoint por ID",
    description="Elimina un registro de estado de endpoint de la base de datos según su ID."
)
async def delete_endpoint_state(state_id: str, service: EndpointStateService = Depends(get_endpoint_state_service)):
    return await service.delete_state(state_id)