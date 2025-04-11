# cryptomesh/controllers/endpoints_controller.py
from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import EndpointModel
from cryptomesh.services.endpoints_services import EndpointsService
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.db import get_collection

router = APIRouter()

def get_endpoints_service() -> EndpointsService:
    collection = get_collection("endpoints")
    repository = EndpointsRepository(collection)
    sp_collection = get_collection("security_policies")
    sp_repository = SecurityPolicyRepository(sp_collection)
    security_policy_service = SecurityPolicyService(sp_repository)
    return EndpointsService(repository, security_policy_service)

@router.post(
    "/endpoints/",
    response_model=EndpointModel,
    response_model_by_alias=True,
    summary="Crear un nuevo endpoint",
    description="Crea un nuevo endpoint en la base de datos."
)
async def create_endpoint(endpoint: EndpointModel, service: EndpointsService = Depends(get_endpoints_service)):
    return await service.create_endpoint(endpoint)

@router.get(
    "/endpoints/",
    response_model=List[EndpointModel],
    response_model_by_alias=True,
    summary="Obtener todos los endpoints",
    description="Recupera todos los endpoints almacenados en la base de datos."
)
async def get_all_endpoints(service: EndpointsService = Depends(get_endpoints_service)):
    return await service.list_endpoints()

@router.get(
    "/endpoints/{endpoint_id}",
    response_model=EndpointModel,
    response_model_by_alias=True,
    summary="Obtener un endpoint por ID",
    description="Devuelve un endpoint específico dado su ID único."
)
async def get_endpoint(endpoint_id: str, service: EndpointsService = Depends(get_endpoints_service)):
    return await service.get_endpoint(endpoint_id)

@router.put(
    "/endpoints/{endpoint_id}",
    response_model=EndpointModel,
    summary="Actualizar un endpoint por ID",
    description="Actualiza completamente un endpoint existente."
)
async def update_endpoint(endpoint_id: str, updated_endpoint: EndpointModel, service: EndpointsService = Depends(get_endpoints_service)):
    update_data = updated_endpoint.dict(by_alias=True, exclude_unset=True)
    return await service.update_endpoint(endpoint_id, update_data)

@router.delete(
    "/endpoints/{endpoint_id}",
    summary="Eliminar un endpoint por ID",
    description="Elimina un endpoint de la base de datos según su ID."
)
async def delete_endpoint(endpoint_id: str, service: EndpointsService = Depends(get_endpoints_service)):
    return await service.delete_endpoint(endpoint_id)


