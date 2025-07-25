from fastapi import APIRouter, Depends, status, Response
from typing import List
from cryptomesh.models import FunctionResultModel
from cryptomesh.services.function_result_service import FunctionResultService
from cryptomesh.repositories.function_result_repository import FunctionResultRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
import time as T

L = get_logger(__name__)
router = APIRouter()

def get_function_result_service() -> FunctionResultService:
    collection = get_collection("function_results")
    repository = FunctionResultRepository(collection)
    return FunctionResultService(repository)

@router.post(
    "/function-results/",
    response_model=FunctionResultModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo function result",
    description="Crea un nuevo registro de resultado para una función en la base de datos."
)
async def create_function_result(result: FunctionResultModel, svc: FunctionResultService = Depends(get_function_result_service)):
    t1 = T.time()
    response = await svc.create_result(result)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION_RESULT.CREATED",
        "state_id": result.state_id,
        "time": elapsed
    })
    return response

@router.get(
    "/function-results/",
    response_model=List[FunctionResultModel],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Listar todos los function results",
    description="Recupera todos los registros de resultados de funciones almacenados en la base de datos."
)
async def list_function_results(svc: FunctionResultService = Depends(get_function_result_service)):
    t1 = T.time()
    results = await svc.list_results()
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.FUNCTION_RESULT.LISTED",
        "count": len(results),
        "time": elapsed
    })
    return results

@router.get(
    "/function-results/{result_id}",
    response_model=FunctionResultModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener function result por ID",
    description="Devuelve un registro de resultado de función específico dado su ID."
)
async def get_function_result(result_id: str, svc: FunctionResultService = Depends(get_function_result_service)):
    t1 = T.time()
    result = await svc.get_result(result_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION_RESULT.FETCHED",
        "result_id": result_id,
        "time": elapsed
    })
    return result

@router.put(
    "/function-results/{result_id}",
    response_model=FunctionResultModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar function result por ID",
    description="Actualiza un registro de resultado de función existente."
)
async def update_function_result(result_id: str, updated: FunctionResultModel, svc: FunctionResultService = Depends(get_function_result_service)):
    update_data = updated.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    response = await svc.update_result(result_id, update_data)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION_RESULT.UPDATED",
        "result_id": result_id,
        "updates": update_data,
        "time": elapsed
    })
    return response

@router.delete(
    "/function-results/{result_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar function result por ID",
    description="Elimina un registro de resultado de función de la base de datos según su ID."
)
async def delete_function_result(result_id: str, svc: FunctionResultService = Depends(get_function_result_service)):
    t1 = T.time()
    await svc.delete_result(result_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION_RESULT.DELETED",
        "result_id": result_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)
