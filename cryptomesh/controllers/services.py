from fastapi import APIRouter,Depends
from typing import List
from models import ServiceModel
from cryptomesh.services import ServicesService
from cryptomesh.repositories import ServicesRepository
from cryptomesh.db import get_collection


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

