import time as T
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
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
        if await self.repository.get_by_id(microservice.microservice_id, id_field="microservice_id"):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "MICROSERVICE.CREATE.FAIL",
                "reason": "Already exists",
                "microservice_id": microservice.microservice_id,
                "time": elapsed
            })
            raise ValidationError(f"Microservice '{microservice.microservice_id}' already exists")

        created = await self.repository.create(microservice)
        elapsed = round(T.time() - t1, 4)

        if not created:
            L.error({
                "event": "MICROSERVICE.CREATE.FAIL",
                "reason": "Failed to create",
                "microservice_id": microservice.microservice_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create microservice '{microservice.microservice_id}'")

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
        if not await self.repository.get_by_id(microservice_id, id_field="microservice_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "MICROSERVICE.UPDATE.NOT_FOUND",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise NotFoundError(microservice_id)

        updated = await self.repository.update({"microservice_id": microservice_id}, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "MICROSERVICE.UPDATE.FAIL",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update microservice '{microservice_id}'")

        L.info({
            "event": "MICROSERVICE.UPDATED",
            "microservice_id": microservice_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_microservice(self, microservice_id: str) -> dict:
        t1 = T.time()
        if not await self.repository.get_by_id(microservice_id, id_field="microservice_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "MICROSERVICE.DELETE.NOT_FOUND",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise NotFoundError(microservice_id)

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

