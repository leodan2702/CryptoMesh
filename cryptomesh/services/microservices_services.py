from fastapi import HTTPException
from typing import List
from cryptomesh.models import MicroserviceModel
from cryptomesh.repositories.microservices_repository import MicroservicesRepository

class MicroservicesService:
    def __init__(self, repository: MicroservicesRepository):
        self.repository = repository

    async def create_microservice(self, microservice: MicroserviceModel) -> MicroserviceModel:
        # Se usa el campo "id" en la búsqueda (según tu repositorio)
        if await self.repository.get_by_id(microservice.id):
            raise HTTPException(status_code=400, detail="Microservicio ya existe")
        created = await self.repository.create(microservice)
        if not created:
            raise HTTPException(status_code=500, detail="Error al crear el microservicio")
        return created

    async def list_microservices(self) -> List[MicroserviceModel]:
        return await self.repository.get_all()

    async def get_microservice(self, microservice_id: str) -> MicroserviceModel:
        ms = await self.repository.get_by_id(microservice_id)
        if not ms:
            raise HTTPException(status_code=404, detail="Microservicio no encontrado")
        return ms

    async def update_microservice(self, microservice_id: str, updates: dict) -> MicroserviceModel:
        if not await self.repository.get_by_id(microservice_id):
            raise HTTPException(status_code=404, detail="Microservicio no encontrado")
        updated = await self.repository.update(microservice_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Error al actualizar el microservicio")
        return updated

    async def delete_microservice(self, microservice_id: str) -> dict:
        if not await self.repository.get_by_id(microservice_id):
            raise HTTPException(status_code=404, detail="Microservicio no encontrado")
        success = await self.repository.delete(microservice_id)
        if not success:
            raise HTTPException(status_code=500, detail="Error al eliminar el microservicio")
        return {"detail": f"Microservicio '{microservice_id}' eliminado"}

