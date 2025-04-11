from fastapi import HTTPException
from typing import List
from cryptomesh.models import StorageModel
from cryptomesh.repositories.storage_repository import StorageRepository

class StorageService:
    def __init__(self, repository: StorageRepository):
        self.repository = repository

    async def create_storage(self, storage: StorageModel) -> StorageModel:
        if await self.repository.get_by_id(storage.storage_id):
            raise HTTPException(status_code=400, detail="Storage already exists")
        created = await self.repository.create(storage)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create storage")
        return created

    async def list_storage(self) -> List[StorageModel]:
        return await self.repository.get_all()

    async def get_storage(self, storage_id: str) -> StorageModel:
        storage = await self.repository.get_by_id(storage_id)
        if not storage:
            raise HTTPException(status_code=404, detail="Storage not found")
        return storage

    async def update_storage(self, storage_id: str, updates: dict) -> StorageModel:
        if not await self.repository.get_by_id(storage_id):
            raise HTTPException(status_code=404, detail="Storage not found")
        updated = await self.repository.update(storage_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update storage")
        return updated

    async def delete_storage(self, storage_id: str) -> dict:
        if not await self.repository.get_by_id(storage_id):
            raise HTTPException(status_code=404, detail="Storage not found")
        success = await self.repository.delete(storage_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete storage")
        return {"detail": f"Storage '{storage_id}' deleted"}

