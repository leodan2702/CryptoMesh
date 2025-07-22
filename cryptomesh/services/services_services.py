import time as T
from cryptomesh.models import ServiceModel
from cryptomesh.repositories.services_repository import ServicesRepository
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

class ServicesService:
    def __init__(self, repository: ServicesRepository):
        self.repository = repository

    async def create_service(self, data: ServiceModel):
        t1 = T.time()
        existing = await self.repository.get_by_id(data.service_id)
        elapsed = round(T.time() - t1, 4)

        if existing:
            L.error({
                "event": "SERVICE.CREATE.FAIL",
                "reason": "Already exists",
                "service_id": data.service_id,
                "time": elapsed
            })
            raise ValidationError(f"Service '{data.service_id}' already exists")
        
        service = await self.repository.create(data)
        elapsed = round(T.time() - t1, 4)

        if not service:
            L.error({
                "event": "SERVICE.CREATE.FAIL",
                "reason": "Failed to create",
                "service_id": data.service_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create service '{data.service_id}'")
        
        L.info({
            "event": "SERVICE.CREATED",
            "service_id": data.service_id,
            "time": elapsed
        })
        return service

    async def list_services(self):
        t1 = T.time()
        services = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)
        L.info({
            "event": "SERVICE.LISTED",
            "count": len(services),
            "time": elapsed
        })
        return services

    async def get_service(self, service_id: str):
        t1 = T.time()
        service = await self.repository.get_by_id(service_id)
        elapsed = round(T.time() - t1, 4)

        if not service:
            L.warning({
                "event": "SERVICE.GET.NOT_FOUND",
                "service_id": service_id,
                "time": elapsed
            })
            raise NotFoundError(service_id)

        L.info({
            "event": "SERVICE.FETCHED",
            "service_id": service_id,
            "time": elapsed
        })
        return service

    async def update_service(self, service_id: str, updates: dict):
        t1 = T.time()
        existing = await self.repository.get_by_id(service_id)
        if not existing:
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "SERVICE.UPDATE.NOT_FOUND",
                "service_id": service_id,
                "time": elapsed
            })
            raise NotFoundError(service_id)

        updated = await self.repository.update(service_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "SERVICE.UPDATE.FAIL",
                "service_id": service_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update service '{service_id}'")

        L.info({
            "event": "SERVICE.UPDATED",
            "service_id": service_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_service(self, service_id: str):
        t1 = T.time()
        existing = await self.repository.get_by_id(service_id)
        if not existing:
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "SERVICE.DELETE.NOT_FOUND",
                "service_id": service_id,
                "time": elapsed
            })
            raise NotFoundError(service_id)

        success = await self.repository.delete(service_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "SERVICE.DELETE.FAIL",
                "service_id": service_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to delete service '{service_id}'")

        L.info({
            "event": "SERVICE.DELETED",
            "service_id": service_id,
            "time": elapsed
        })
        return {"detail": f"Service '{service_id}' deleted"}

