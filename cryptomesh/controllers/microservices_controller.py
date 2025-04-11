from fastapi import APIRouter, Depends, HTTPException
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.services.microservices_services import MicroservicesService
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.db import get_collection  # Función que retorna la colección "microservices" de MongoDB

router = APIRouter()

def get_microservices_service() -> MicroservicesService:
    collection = get_collection("microservices")
    repository = MicroservicesRepository(collection)
    return MicroservicesService(repository)

@router.post(
    "/microservices/",
    response_model=MicroserviceModel,
    response_model_by_alias=True,
    summary="Crear un nuevo microservicio",
    description="Crea un nuevo microservicio en la base de datos. El ID debe ser único."
)
async def create_microservice(
    microservice: MicroserviceModel, 
    ms_service: MicroservicesService = Depends(get_microservices_service)
):
    return await ms_service.create_microservice(microservice)

@router.get(
    "/microservices/",
    response_model=List[MicroserviceModel],
    response_model_by_alias=True,
    summary="Obtener todos los microservicios",
    description="Recupera todos los microservicios almacenados en la base de datos."
)
async def list_microservices(ms_service: MicroservicesService = Depends(get_microservices_service)):
    return await ms_service.list_microservices()

@router.get(
    "/microservices/{microservice_id}",
    response_model=MicroserviceModel,
    response_model_by_alias=True,
    summary="Obtener un microservicio por ID",
    description="Devuelve un microservicio específico dado su ID único."
)
async def get_microservice(
    microservice_id: str, 
    ms_service: MicroservicesService = Depends(get_microservices_service)
):
    ms = await ms_service.get_microservice(microservice_id)
    if not ms:
        raise HTTPException(status_code=404, detail="Microservicio no encontrado")
    return ms

@router.put(
    "/microservices/{microservice_id}",
    response_model=MicroserviceModel,
    summary="Actualizar un microservicio por ID",
    description="Actualiza completamente un microservicio existente."
)
async def update_microservice(
    microservice_id: str, 
    updated: MicroserviceModel, 
    ms_service: MicroservicesService = Depends(get_microservices_service)
):
    update_data = updated.dict(by_alias=True, exclude_unset=True)
    updated_ms = await ms_service.update_microservice(microservice_id, update_data)
    if not updated_ms:
        raise HTTPException(status_code=404, detail="Microservicio no encontrado o error al actualizar")
    return updated_ms

@router.delete(
    "/microservices/{microservice_id}",
    summary="Eliminar un microservicio por ID",
    description="Elimina un microservicio de la base de datos según su ID."
)
async def delete_microservice(
    microservice_id: str, 
    ms_service: MicroservicesService = Depends(get_microservices_service)
):
    return await ms_service.delete_microservice(microservice_id)

