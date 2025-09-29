# cryptomesh/controllers/hierarchy_controller.py
from fastapi import APIRouter, Depends
from typing import List

from cryptomesh.dtos.hierarchy_dto import (
    ServiceHierarchyDTO,
    MicroserviceHierarchyDTO,
    ActiveObjectHierarchyDTO,
    FunctionHierarchyDTO,
    ParameterDTO,
)
from cryptomesh.services.services_services import ServicesService
from cryptomesh.services.microservices_services import MicroservicesService
from cryptomesh.services.activeobjects_service import ActiveObjectsService

from cryptomesh.repositories.services_repository import ServicesRepository
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.repositories.activeobjects_repository import ActiveObjectsRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)
router = APIRouter()

# -------------------------------
# Factories para inyección de dependencias
# -------------------------------
def get_services_service() -> ServicesService:
    collection = get_collection("services")
    repo = ServicesRepository(collection)
    return ServicesService(repo)

def get_microservices_service() -> MicroservicesService:
    collection = get_collection("microservices")
    repo = MicroservicesRepository(collection)
    return MicroservicesService(repo)

def get_active_objects_service() -> ActiveObjectsService:
    collection = get_collection("active_objects")
    repo = ActiveObjectsRepository(collection)
    return ActiveObjectsService(repo)


# -------------------------------
# Endpoint de jerarquía
# -------------------------------
@router.get("/hierarchy", response_model=List[ServiceHierarchyDTO])
async def get_hierarchy(
    services_service: ServicesService = Depends(get_services_service),
    microservices_service: MicroservicesService = Depends(get_microservices_service),
    active_objects_service: ActiveObjectsService = Depends(get_active_objects_service),
):
    """
    Devuelve la jerarquía completa:
    Service -> Microservice -> ActiveObject -> Functions -> Params
    """
    hierarchy: List[ServiceHierarchyDTO] = []

    services = await services_service.list_services()

    for svc in services:
        svc_microservices = await microservices_service.list_by_service(svc.service_id)
        microservices_dto: List[MicroserviceHierarchyDTO] = []

        for ms in svc_microservices:
            ms_active_objects = await active_objects_service.list_by_microservice(ms.microservice_id)
            active_objects_dto: List[ActiveObjectHierarchyDTO] = []

            for ao in ms_active_objects:
                functions_dto: List[FunctionHierarchyDTO] = []

                for f in ao.functions:
                    # Convertimos init y call params en DTOs
                    init_params = [
                        ParameterDTO(**p.model_dump()) if hasattr(p, "model_dump") else ParameterDTO(**p)
                        for p in f.init_params
                    ]
                    call_params = [
                        ParameterDTO(**p.model_dump()) if hasattr(p, "model_dump") else ParameterDTO(**p)
                        for p in f.call_params
                    ]

                    functions_dto.append(
                        FunctionHierarchyDTO(
                            function_id=f.function_id,
                            name=f.name,
                            init_params=init_params,
                            call_params=call_params,
                        )
                    )


                active_objects_dto.append(
                    ActiveObjectHierarchyDTO(
                        active_object_id=ao.active_object_id,
                        object_name=ao.axo_class_name,
                        alias=ao.axo_alias,
                        version=ao.axo_version,
                        functions=functions_dto,
                    )
                )

            microservices_dto.append(
                MicroserviceHierarchyDTO(
                    microservice_id=ms.microservice_id,
                    microservice_name=ms.name,
                    active_objects=active_objects_dto,
                )
            )

        hierarchy.append(
            ServiceHierarchyDTO(
                service_id=svc.service_id,
                service_name=svc.name,
                microservices=microservices_dto,
            )
        )

    L.info({"event": "API.HIERARCHY.FETCHED", "services": len(services)})
    return hierarchy
