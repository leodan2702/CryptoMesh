import time as T
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.repositories.services_repository import ServicesRepository
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

L = get_logger(__name__)

class MicroservicesService:
    """
    Servicio encargado de gestionar los microservicios en la base de datos.
    """

    def __init__(self, repository: MicroservicesRepository):
        self.repository = repository

    async def create_microservice(self, microservice: MicroserviceModel) -> MicroserviceModel:
        t1 = T.time()

        # Verificar si ya existe
        existing = await self.repository.get_by_id(microservice.microservice_id, id_field="microservice_id")
        if existing:
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "MICROSERVICE.CREATE.FAIL",
                "reason": "Already exists",
                "microservice_id": microservice.microservice_id,
                "time": elapsed
            })
            raise ValidationError(f"Microservice '{microservice.microservice_id}' already exists")

        # Crear microservicio
        created = await self.repository.create(microservice)
        if not created:
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "MICROSERVICE.CREATE.FAIL",
                "reason": "Failed to create",
                "microservice_id": microservice.microservice_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create microservice '{microservice.microservice_id}'")

        #Actualizar service padre
        service_collection = get_collection("services")
        service_repo = ServicesRepository(service_collection)

        service_model = await service_repo.get_by_id(microservice.service_id, id_field="service_id")
        if service_model:
            try:
                result = await service_repo.update_push_microservice(
                    service_id=microservice.service_id,
                    microservice_id=microservice.microservice_id
                )
                L.info({
                    "event": "MICROSERVICE.CREATE.SERVICE.UPDATED",
                    "microservice_id": microservice.microservice_id,
                    "service_id": microservice.service_id,
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count
                })
            except Exception as e:
                L.error({
                    "event": "MICROSERVICE.CREATE.SERVICE.UPDATE_FAIL",
                    "microservice_id": microservice.microservice_id,
                    "service_id": microservice.service_id,
                    "reason": str(e)
                })
        else:
            L.warning({
                "event": "MICROSERVICE.CREATE.SERVICE.NOT_FOUND",
                "microservice_id": microservice.microservice_id,
                "service_id": microservice.service_id
            })

        elapsed = round(T.time() - t1, 4)
        L.info({
            "event": "MICROSERVICE.CREATED",
            "microservice_id": microservice.microservice_id,
            "time": elapsed
        })
        return created

    async def list_microservices(self) -> List[MicroserviceModel]:
        t1 = T.time()
        microservices = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)
        L.debug({
            "event": "MICROSERVICE.LISTED",
            "count": len(microservices),
            "time": elapsed
        })
        return microservices

    async def get_microservice(self, microservice_id: str) -> MicroserviceModel:
        t1 = T.time()
        ms = await self.repository.get_by_id(microservice_id, id_field="microservice_id")
        elapsed = round(T.time() - t1, 4)

        if not ms:
            L.warning({
                "event": "MICROSERVICE.GET.NOT_FOUND",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise NotFoundError(microservice_id)

        L.info({
            "event": "MICROSERVICE.FETCHED",
            "microservice_id": microservice_id,
            "time": elapsed
        })
        return ms

    async def update_microservice(self, microservice_id: str, updates: dict) -> MicroserviceModel:
        t1 = T.time()
        
        ms = await self.repository.get_by_id(microservice_id, id_field="microservice_id")
        if not ms:
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "MICROSERVICE.UPDATE.NOT_FOUND",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise NotFoundError(microservice_id)

        old_service_id = ms.service_id
        new_service_id = updates.get("service_id", old_service_id)

        # Actualizar microservicio
        updated = await self.repository.update({"microservice_id": microservice_id}, updates)
        if not updated:
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "MICROSERVICE.UPDATE.FAIL",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update microservice '{microservice_id}'")

        # Actualizar services si cambió
        if new_service_id != old_service_id:
            service_collection = get_collection("services")
            service_repo = ServicesRepository(service_collection)

            # Quitar de service antiguo
            await service_repo.update_pull_microservice(old_service_id, microservice_id)
            
            # Agregar a service nuevo
            await service_repo.update_push_microservice(new_service_id, microservice_id)

        elapsed = round(T.time() - t1, 4)
        L.info({
            "event": "MICROSERVICE.UPDATED",
            "microservice_id": microservice_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_microservice(self, microservice_id: str) -> dict:
        t1 = T.time()

        # Obtener el microservicio para conocer su service_id
        ms = await self.repository.get_by_id(microservice_id, id_field="microservice_id")
        if not ms:
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "MICROSERVICE.DELETE.NOT_FOUND",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise NotFoundError(microservice_id)

        # Eliminar referencia del service padre
        service_collection = get_collection("services")
        service_repo = ServicesRepository(service_collection)
        try:
            await service_repo.update_pull_microservice(ms.service_id, microservice_id)
            L.info({
                "event": "MICROSERVICE.DELETE.SERVICE.UPDATED",
                "microservice_id": microservice_id,
                "service_id": ms.service_id
            })
        except Exception as e:
            L.error({
                "event": "MICROSERVICE.DELETE.SERVICE.UPDATE_FAIL",
                "microservice_id": microservice_id,
                "service_id": ms.service_id,
                "reason": str(e)
            })

        # Eliminar microservicio
        success = await self.repository.delete({"microservice_id": microservice_id})
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "MICROSERVICE.DELETE.FAIL",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to delete microservice '{microservice_id}'")

        L.info({
            "event": "MICROSERVICE.DELETED",
            "microservice_id": microservice_id,
            "time": elapsed
        })
        return {"detail": f"Microservice '{microservice_id}' deleted"}


    async def list_by_service(self, service_id: str) -> List[MicroserviceModel]:
        """
        Devuelve todos los microservicios que pertenecen a un servicio especifico
        """
        try:
            return await self.repository.get_by_filter({"service_id": service_id})
        except Exception as e:
            L.error({
                "event": "SERVICE.MICROSERVICES.LIST_BY_SERVICE.FAIL","service_id": service_id, "reason": str(e)
            })
            raise CryptoMeshError(f"Failed to list microservices for service '{service_id}'")

