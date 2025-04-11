from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import FunctionStateModel
from cryptomesh.services.function_state_service import FunctionStateService
from cryptomesh.repositories.function_state_repository import FunctionStateRepository
from cryptomesh.db import get_collection

router = APIRouter()

def get_function_state_service() -> FunctionStateService:
    collection = get_collection("function_states")
    repository = FunctionStateRepository(collection)
    return FunctionStateService(repository)

@router.post(
    "/function-states/",
    response_model=FunctionStateModel,
    summary="Crear un nuevo estado de función",
    description="Crea un nuevo registro de estado para una función en la base de datos."
)
async def create_function_state(state: FunctionStateModel, service: FunctionStateService = Depends(get_function_state_service)):
    return await service.create_state(state)

@router.get(
    "/function-states/",
    response_model=List[FunctionStateModel],
    summary="Listar todos los estados de función",
    description="Recupera todos los registros de estado de funciones almacenados en la base de datos."
)
async def list_function_states(service: FunctionStateService = Depends(get_function_state_service)):
    return await service.list_states()

@router.get(
    "/function-states/{state_id}",
    response_model=FunctionStateModel,
    summary="Obtener estado de función por ID",
    description="Devuelve un registro de estado de función específico dado su ID."
)
async def get_function_state(state_id: str, service: FunctionStateService = Depends(get_function_state_service)):
    return await service.get_state(state_id)

@router.put(
    "/function-states/{state_id}",
    response_model=FunctionStateModel,
    summary="Actualizar estado de función por ID",
    description="Actualiza completamente un registro de estado de función existente."
)
async def update_function_state(state_id: str, updated: FunctionStateModel, service: FunctionStateService = Depends(get_function_state_service)):
    update_data = updated.dict(by_alias=True, exclude_unset=True)
    return await service.update_state(state_id, update_data)

@router.delete(
    "/function-states/{state_id}",
    summary="Eliminar estado de función por ID",
    description="Elimina un registro de estado de función de la base de datos según su ID."
)
async def delete_function_state(state_id: str, service: FunctionStateService = Depends(get_function_state_service)):
    return await service.delete_state(state_id)