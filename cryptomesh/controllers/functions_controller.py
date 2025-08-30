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
from cryptomesh.dtos.functions_dto import FunctionCreateDTO, FunctionResponseDTO, FunctionUpdateDTO

router = APIRouter()
L = get_logger(__name__)

def get_functions_service() -> FunctionsService:
    collection = get_collection("functions")
    repository = FunctionsRepository(collection)
    return FunctionsService(repository)

@router.post(
    "/functions/",
    response_model=FunctionResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva función",
    description="Crea una nueva función en la base de datos."
)
async def create_function(dto:FunctionCreateDTO, svc: FunctionsService = Depends(get_functions_service)):
    t1 = T.time()
    try:
        model = dto.to_model()
        created = await svc.create_function(model)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=e.to_dict())
    except CryptoMeshError as e:
        raise HTTPException(status_code=500, detail=e.to_dict())
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.FUNCTION.CREATED",
        "function_id": created.function_id,
        "time": elapsed
    })
    return FunctionResponseDTO.from_model(created)

@router.get(
    "/functions/",
    response_model=List[FunctionResponseDTO],
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
    return [FunctionResponseDTO.from_model(f) for f in functions]

@router.get(
    "/functions/{function_id}/",
    response_model=FunctionResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener una función por ID",
    description="Devuelve una función específica dada su ID única."
)
async def get_function(function_id: str, svc: FunctionsService = Depends(get_functions_service)):
    t1 = T.time()
    try:
        func = await svc.get_function(function_id)
        if not func:
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
    return FunctionResponseDTO.from_model(func)

@router.put(
    "/functions/{function_id}/",
    response_model=FunctionResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una función por ID",
    description="Actualiza completamente una función existente."
)
async def update_function(function_id: str, dto: FunctionUpdateDTO, svc: FunctionsService = Depends(get_functions_service)):
    t1 = T.time()
    try:
        existing = await svc.get_function(function_id)
        if not existing:
            raise NotFoundError(function_id)

        updated_model = FunctionUpdateDTO.apply_updates(dto, existing)
        updated = await svc.update_function(function_id, updated_model.model_dump(by_alias=True))

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
        "time": elapsed
    })
    return FunctionResponseDTO.from_model(updated)

@router.delete(
    "/functions/{function_id}/",
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
