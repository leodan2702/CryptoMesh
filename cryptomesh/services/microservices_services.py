import time as T
from fastapi import HTTPException
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.repositories.microservices_repository import MicroservicesRepository
from cryptomesh.log import Log

# Logger configurado
L = Log(name=__name__)

class MicroservicesService:
    """
    Servicio encargado de gestionar los microservicios en la base de datos.
    """

    def __init__(self, repository: MicroservicesRepository):
        self.repository = repository

    async def create_microservice(self, microservice: MicroserviceModel) -> MicroserviceModel:
        t1 = T.time()
        if await self.repository.get_by_id(microservice.microservice_id):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "MICROSERVICE.CREATE.FAIL",
                "reason": "Already exists",
                "microservice_id": microservice.microservice_id,
                "time": elapsed
            })
            raise HTTPException(status_code=400, detail="Microservice already exists")

        created = await self.repository.create(microservice)
        elapsed = round(T.time() - t1, 4)

        if not created:
            L.error({
                "event": "MICROSERVICE.CREATE.FAIL",
                "reason": "Failed to create",
                "microservice_id": microservice.microservice_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to create microservice")

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
        ms = await self.repository.get_by_id(microservice_id)
        elapsed = round(T.time() - t1, 4)

        if not ms:
            L.warning({
                "event": "MICROSERVICE.GET.NOT_FOUND",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Microservice not found")

        L.info({
            "event": "MICROSERVICE.FETCHED",
            "microservice_id": microservice_id,
            "time": elapsed
        })
        return ms

    async def update_microservice(self, microservice_id: str, updates: dict) -> MicroserviceModel:
        t1 = T.time()
        if not await self.repository.get_by_id(microservice_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "MICROSERVICE.UPDATE.NOT_FOUND",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Microservice not found")

        updated = await self.repository.update(microservice_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "MICROSERVICE.UPDATE.FAIL",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to update microservice")

        L.info({
            "event": "MICROSERVICE.UPDATED",
            "microservice_id": microservice_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_microservice(self, microservice_id: str) -> dict:
        t1 = T.time()
        if not await self.repository.get_by_id(microservice_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "MICROSERVICE.DELETE.NOT_FOUND",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Microservice not found")

        success = await self.repository.delete(microservice_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "MICROSERVICE.DELETE.FAIL",
                "microservice_id": microservice_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to delete microservice")

        L.info({
            "event": "MICROSERVICE.DELETED",
            "microservice_id": microservice_id,
            "time": elapsed
        })
        return {"detail": f"Microservice '{microservice_id}' deleted"}

