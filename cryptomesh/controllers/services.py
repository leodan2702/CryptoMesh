from fastapi import APIRouter,Depends
from typing import List
from cryptomesh.models import ServiceModel
from cryptomesh.services import ServicesService
from cryptomesh.repositories import ServicesRepository
from cryptomesh.db import get_collection
from fastapi import status
from fastapi import Body


router = APIRouter()

def get_service_service()->ServicesService:
    service = ServicesService(
        repository= ServicesRepository(
            collection= get_collection("services")
        )
    )
    return service

@router.get("/services", response_model=List[ServiceModel])

async def get_services(
    services_service: ServicesService = Depends(get_service_service)
):
    """
    Retrieve a list of all services.
    """
    return await services_service.get_all_services()

@router.post("/services", response_model=ServiceModel, status_code=status.HTTP_201_CREATED)
async def create_service(
    service: ServiceModel = Body(...),
    services_service: ServicesService = Depends(get_service_service)
):
    """
    Create a new service and return the created service.
    """
    return await services_service.create_service(service)

