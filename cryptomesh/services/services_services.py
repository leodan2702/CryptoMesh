from fastapi import HTTPException
from cryptomesh.models import ServiceModel
from cryptomesh.repositories.services_repository import ServicesRepository

class ServicesService:
    def __init__(self, repository: ServicesRepository):
        self.repository = repository

    async def create_service(self, data: ServiceModel):
        if await self.repository.get_by_id(data.service_id):
            raise HTTPException(status_code=400, detail="Service already exists")
        service = await self.repository.create(data)
        if not service:
            raise HTTPException(status_code=500, detail="Failed to create service")
        return service

    async def list_services(self):
        return await self.repository.get_all()

    async def get_service(self, service_id: str):
        service = await self.repository.get_by_id(service_id)
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service

    async def update_service(self, service_id: str, updates: dict):
        if not await self.repository.get_by_id(service_id):
            raise HTTPException(status_code=404, detail="Service not found")
        updated = await self.repository.update(service_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update service")
        return updated

    async def delete_service(self, service_id: str):
        if not await self.repository.get_by_id(service_id):
            raise HTTPException(status_code=404, detail="Service not found")
        success = await self.repository.delete(service_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete service")
        return {"detail": f"Service '{service_id}' deleted"}
