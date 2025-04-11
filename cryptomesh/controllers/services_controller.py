from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import ServiceModel
from cryptomesh.services.services_services import ServicesService
from cryptomesh.repositories.services_repository import ServicesRepository
from cryptomesh.db import get_collection

router = APIRouter()

def get_services_service() -> ServicesService:
    collection = get_collection("services")
    repository = ServicesRepository(collection)
    return ServicesService(repository)

@router.post(
    "/services/",
    response_model=ServiceModel,
    response_model_by_alias=True,
    summary="Crear un nuevo service",
    description="Crea un nuevo service en la base de datos. El ID debe ser único."
)
async def create_service(service: ServiceModel, service_svc: ServicesService = Depends(get_services_service)):
    return await service_svc.create_service(service)

@router.get(
    "/services/",
    response_model=List[ServiceModel],
    response_model_by_alias=True,
    summary="Obtener todos los services",
    description="Recupera todos los services almacenados en la base de datos."
)
async def get_all_services(service_svc: ServicesService = Depends(get_services_service)):
    return await service_svc.list_services()

@router.get(
    "/services/{service_id}",
    response_model=ServiceModel,
    response_model_by_alias=True,
    summary="Obtener un service por ID",
    description="Devuelve un service específico dado su ID único."
)
async def get_service(service_id: str, service_svc: ServicesService = Depends(get_services_service)):
    return await service_svc.get_service(service_id)

@router.put(
    "/services/{service_id}",
    response_model=ServiceModel,
    summary="Actualizar un service por ID",
    description="Actualiza completamente un service existente."
)
async def update_service(service_id: str, updated: ServiceModel, service_svc: ServicesService = Depends(get_services_service)):
    update_data = updated.dict(by_alias=True, exclude_unset=True)
    return await service_svc.update_service(service_id, update_data)

@router.delete(
    "/services/{service_id}",
    summary="Eliminar un service por ID",
    description="Elimina un service de la base de datos según su ID."
)
async def delete_service(service_id: str, service_svc: ServicesService = Depends(get_services_service)):
    return await service_svc.delete_service(service_id)
