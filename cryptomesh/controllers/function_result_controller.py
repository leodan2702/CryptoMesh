from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import FunctionResultModel
from cryptomesh.services.function_result_service import FunctionResultService
from cryptomesh.repositories.function_result_repository import FunctionResultRepository
from cryptomesh.db import get_collection

router = APIRouter()

def get_function_result_service() -> FunctionResultService:
    collection = get_collection("function_results")
    repository = FunctionResultRepository(collection)
    return FunctionResultService(repository)

@router.post(
    "/function-results/",
    response_model=FunctionResultModel,
    summary="Crear un nuevo function result",
    description="Crea un nuevo registro de resultado para una función en la base de datos."
)
async def create_function_result(result: FunctionResultModel, service: FunctionResultService = Depends(get_function_result_service)):
    return await service.create_result(result)

@router.get(
    "/function-results/",
    response_model=List[FunctionResultModel],
    summary="Listar todos los function results",
    description="Recupera todos los registros de resultados de funciones almacenados en la base de datos."
)
async def list_function_results(service: FunctionResultService = Depends(get_function_result_service)):
    return await service.list_results()

@router.get(
    "/function-results/{result_id}",
    response_model=FunctionResultModel,
    summary="Obtener function result por ID",
    description="Devuelve un registro de resultado de función específico dado su ID."
)
async def get_function_result(result_id: str, service: FunctionResultService = Depends(get_function_result_service)):
    return await service.get_result(result_id)

@router.put(
    "/function-results/{result_id}",
    response_model=FunctionResultModel,
    summary="Actualizar function result por ID",
    description="Actualiza un registro de resultado de función existente."
)
async def update_function_result(result_id: str, updated: FunctionResultModel, service: FunctionResultService = Depends(get_function_result_service)):
    update_data = updated.model_dump(by_alias=True, exclude_unset=True)
    return await service.update_result(result_id, update_data)

@router.delete(
    "/function-results/{result_id}",
    summary="Eliminar function result por ID",
    description="Elimina un registro de resultado de función de la base de datos según su ID."
)
async def delete_function_result(result_id: str, service: FunctionResultService = Depends(get_function_result_service)):
    return await service.delete_result(result_id)