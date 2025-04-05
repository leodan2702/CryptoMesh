from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.services.microservices import MicroservicesService
from cryptomesh.repositories.microservices import MicroservicesRepository
from cryptomesh.db import get_collection

router = APIRouter()

def get_microservice_service() -> MicroservicesService:
    service = MicroservicesService(
        repository=MicroservicesRepository(
            collection=get_collection("microservices")
        )
    )
    return service

@router.get("/microservices", response_model=List[MicroserviceModel])
async def get_microservices(
    microservices_service: MicroservicesService = Depends(get_microservice_service)
):
    """
    Retrieve a list of all microservices.
    """
    return await microservices_service.get_all_microservices()
