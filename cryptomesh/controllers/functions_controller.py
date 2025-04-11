# cryptomesh/controllers/functions_controller.py
from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import FunctionModel
from cryptomesh.services.functions_services import FunctionsService
from cryptomesh.repositories.functions_repository import FunctionsRepository
from cryptomesh.db import get_collection

router = APIRouter()

def get_functions_service() -> FunctionsService:
    collection = get_collection("functions")
    repository = FunctionsRepository(collection)
    return FunctionsService(repository)

@router.post(
    "/functions/",
    response_model=FunctionModel,
    response_model_by_alias=True,
    summary="Crear una nueva función",
    description="Crea una nueva función en la base de datos."
)
async def create_function(function: FunctionModel, service: FunctionsService = Depends(get_functions_service)):
    return await service.create_function(function)

@router.get(
    "/functions/",
    response_model=List[FunctionModel],
    response_model_by_alias=True,
    summary="Obtener todas las funciones",
    description="Recupera todas las funciones almacenadas en la base de datos."
)
async def get_all_functions(service: FunctionsService = Depends(get_functions_service)):
    return await service.list_functions()

@router.get(
    "/functions/{function_id}",
    response_model=FunctionModel,
    response_model_by_alias=True,
    summary="Obtener una función por ID",
    description="Devuelve una función específica dada su ID única."
)
async def get_function(function_id: str, service: FunctionsService = Depends(get_functions_service)):
    return await service.get_function(function_id)

@router.put(
    "/functions/{function_id}",
    response_model=FunctionModel,
    summary="Actualizar una función por ID",
    description="Actualiza completamente una función existente."
)
async def update_function(function_id: str, updated_function: FunctionModel, service: FunctionsService = Depends(get_functions_service)):
    update_data = updated_function.dict(by_alias=True, exclude_unset=True)
    return await service.update_function(function_id, update_data)

@router.delete(
    "/functions/{function_id}",
    summary="Eliminar una función por ID",
    description="Elimina una función de la base de datos según su ID."
)
async def delete_function(function_id: str, service: FunctionsService = Depends(get_functions_service)):
    return await service.delete_function(function_id)

