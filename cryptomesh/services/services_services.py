import time as T
from fastapi import HTTPException
from cryptomesh.models import ServiceModel
from cryptomesh.repositories.services_repository import ServicesRepository
from cryptomesh.log import Log

# Logger configurado por nombre de archivo
L = Log(name=__name__)

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
            raise HTTPException(status_code=400, detail="Service already exists")
        
        service = await self.repository.create(data)
        elapsed = round(T.time() - t1, 4)

        if not service:
            L.error({
                "event": "SERVICE.CREATE.FAIL",
                "reason": "Failed to create",
                "service_id": data.service_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to create service")
        
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
            raise HTTPException(status_code=404, detail="Service not found")

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
            raise HTTPException(status_code=404, detail="Service not found")

        updated = await self.repository.update(service_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "SERVICE.UPDATE.FAIL",
                "service_id": service_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to update service")

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
            raise HTTPException(status_code=404, detail="Service not found")

        success = await self.repository.delete(service_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "SERVICE.DELETE.FAIL",
                "service_id": service_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to delete service")

        L.info({
            "event": "SERVICE.DELETED",
            "service_id": service_id,
            "time": elapsed
        })
        return {"detail": f"Service '{service_id}' deleted"}

