from fastapi import APIRouter, Depends, status, Response, HTTPException
from typing import List
from cryptomesh.models import FunctionModel
from cryptomesh.services.functions_services import FunctionsService
from cryptomesh.repositories.functions_repository import FunctionsRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError,
    InvalidYAML,
    CreationError,
    UnauthorizedError,
    FunctionNotFound,
)
import time as T

router = APIRouter()
L = get_logger(__name__)

def get_functions_service() -> FunctionsService:
    collection = get_collection("functions")
    repository = FunctionsRepository(collection)
    return FunctionsService(repository)

@router.post(
    "/functions/",
    response_model=FunctionModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva función",
    description="Crea una nueva función en la base de datos."
)
async def create_function(function: FunctionModel, svc: FunctionsService = Depends(get_functions_service)):
    t1 = T.time()
    try:
        response = await svc.create_function(function)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION.CREATED",
        "function_id": function.function_id,
        "time": elapsed
    })
    return response

@router.get(
    "/functions/",
    response_model=List[FunctionModel],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todas las funciones",
    description="Recupera todas las funciones almacenadas en la base de datos."
)
async def list_functions(svc: FunctionsService = Depends(get_functions_service)):
    t1 = T.time()
    try:
        functions = await svc.list_functions()
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.FUNCTION.LISTED",
        "count": len(functions),
        "time": elapsed
    })
    return functions

@router.get(
    "/functions/{function_id}",
    response_model=FunctionModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener una función por ID",
    description="Devuelve una función específica dada su ID única."
)
async def get_function(function_id: str, svc: FunctionsService = Depends(get_functions_service)):
    t1 = T.time()
    try:
        result = await svc.get_function(function_id)
        if not result:
            raise NotFoundError(function_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.warning({
            "event": "API.FUNCTION.NOT_FOUND",
            "function_id": function_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION.FETCHED",
        "function_id": function_id,
        "time": elapsed
    })
    return result

@router.put(
    "/functions/{function_id}",
    response_model=FunctionModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una función por ID",
    description="Actualiza completamente una función existente."
)
async def update_function(function_id: str, updated_function: FunctionModel, svc: FunctionsService = Depends(get_functions_service)):
    update_data = updated_function.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    try:
        result = await svc.update_function(function_id, update_data)
        if not result:
            raise NotFoundError(function_id)
    except NotFoundError as e:
        elapsed = round(T.time() - t1, 4)
        L.error({
            "event": "API.FUNCTION.UPDATE.FAIL",
            "function_id": function_id,
            "time": elapsed
        })
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION.UPDATED",
        "function_id": function_id,
        "updates": update_data,
        "time": elapsed
    })
    return result

@router.delete(
    "/functions/{function_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una función por ID",
    description="Elimina una función de la base de datos según su ID."
)
async def delete_function(function_id: str, svc: FunctionsService = Depends(get_functions_service)):
    t1 = T.time()
    try:
        await svc.delete_function(function_id)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=e.to_dict())
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION.DELETED",
        "function_id": function_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)
