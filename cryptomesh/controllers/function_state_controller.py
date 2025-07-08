from fastapi import APIRouter, Depends, status, Response
from typing import List
from cryptomesh.models import FunctionStateModel
from cryptomesh.services.function_state_service import FunctionStateService
from cryptomesh.repositories.function_state_repository import FunctionStateRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
import time as T

router = APIRouter()
L = get_logger(__name__)

def get_function_state_service() -> FunctionStateService:
    collection = get_collection("function_states")
    repository = FunctionStateRepository(collection)
    return FunctionStateService(repository)

@router.post(
    "/function-states/",
    response_model=FunctionStateModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo estado de función",
    description="Crea un nuevo registro de estado para una función en la base de datos."
)
async def create_function_state(state: FunctionStateModel, svc: FunctionStateService = Depends(get_function_state_service)):
    t1 = T.time()
    response = await svc.create_state(state)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION_STATE.CREATED",
        "state_id": state.state_id,
        "time": elapsed
    })
    return response

@router.get(
    "/function-states/",
    response_model=List[FunctionStateModel],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Listar todos los estados de función",
    description="Recupera todos los registros de estado de funciones almacenados en la base de datos."
)
async def list_function_states(svc: FunctionStateService = Depends(get_function_state_service)):
    t1 = T.time()
    states = await svc.list_states()
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.FUNCTION_STATE.LISTED",
        "count": len(states),
        "time": elapsed
    })
    return states

@router.get(
    "/function-states/{state_id}",
    response_model=FunctionStateModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener estado de función por ID",
    description="Devuelve un registro de estado de función específico dado su ID."
)
async def get_function_state(state_id: str, svc: FunctionStateService = Depends(get_function_state_service)):
    t1 = T.time()
    result = await svc.get_state(state_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION_STATE.FETCHED",
        "state_id": state_id,
        "time": elapsed
    })
    return result

@router.put(
    "/function-states/{state_id}",
    response_model=FunctionStateModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar estado de función por ID",
    description="Actualiza completamente un registro de estado de función existente."
)
async def update_function_state(state_id: str, updated: FunctionStateModel, svc: FunctionStateService = Depends(get_function_state_service)):
    update_data = updated.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    result = await svc.update_state(state_id, update_data)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION_STATE.UPDATED",
        "state_id": state_id,
        "updates": update_data,
        "time": elapsed
    })
    return result

@router.delete(
    "/function-states/{state_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar estado de función por ID",
    description="Elimina un registro de estado de función de la base de datos según su ID."
)
async def delete_function_state(state_id: str, svc: FunctionStateService = Depends(get_function_state_service)):
    t1 = T.time()
    await svc.delete_state(state_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION_STATE.DELETED",
        "state_id": state_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)


