from fastapi import APIRouter, Depends, HTTPException
from typing import List
from cryptomesh.models import StorageModel
from cryptomesh.services.storage_service import StorageService
from cryptomesh.repositories.storage_repository import StorageRepository
from cryptomesh.db import get_collection  # Asegúrate de que get_collection devuelve la colección "storage" de MongoDB

router = APIRouter()

def get_storage_service() -> StorageService:
    collection = get_collection("storage")
    repository = StorageRepository(collection)
    return StorageService(repository)

@router.post(
    "/storage/",
    response_model=StorageModel,
    summary="Crear un Storage",
    description="Crea un nuevo Storage en la base de datos."
)
async def create_storage(storage: StorageModel, service: StorageService = Depends(get_storage_service)):
    return await service.create_storage(storage)

@router.get(
    "/storage/",
    response_model=List[StorageModel],
    summary="Obtener todos los Storage",
    description="Recupera todos los registros de Storage."
)
async def list_storage(service: StorageService = Depends(get_storage_service)):
    return await service.list_storage()

@router.get(
    "/storage/{storage_id}",
    response_model=StorageModel,
    summary="Obtener Storage por ID",
    description="Devuelve un Storage específico dado su ID."
)
async def get_storage(storage_id: str, service: StorageService = Depends(get_storage_service)):
    return await service.get_storage(storage_id)

@router.put(
    "/storage/{storage_id}",
    response_model=StorageModel,
    summary="Actualizar Storage por ID",
    description="Actualiza completamente un Storage existente."
)
async def update_storage(storage_id: str, updated: StorageModel, service: StorageService = Depends(get_storage_service)):
    update_data = updated.dict(by_alias=True, exclude_unset=True)
    return await service.update_storage(storage_id, update_data)

@router.delete(
    "/storage/{storage_id}",
    summary="Eliminar Storage por ID",
    description="Elimina un Storage de la base de datos según su ID."
)
async def delete_storage(storage_id: str, service: StorageService = Depends(get_storage_service)):
    return await service.delete_storage(storage_id)
