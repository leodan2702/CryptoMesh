from fastapi import HTTPException
from typing import List
from cryptomesh.models import EndpointStateModel
from cryptomesh.repositories.endpoint_state_repository import EndpointStateRepository

class EndpointStateService:
    def __init__(self, repository: EndpointStateRepository):
        self.repository = repository

    async def create_state(self, state: EndpointStateModel) -> EndpointStateModel:
        if await self.repository.get_by_id(state.state_id):
            raise HTTPException(status_code=400, detail="Endpoint state already exists")
        created = await self.repository.create(state)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create endpoint state")
        return created

    async def list_states(self) -> List[EndpointStateModel]:
        return await self.repository.get_all()

    async def get_state(self, state_id: str) -> EndpointStateModel:
        state = await self.repository.get_by_id(state_id)
        if not state:
            raise HTTPException(status_code=404, detail="Endpoint state not found")
        return state

    async def update_state(self, state_id: str, updates: dict) -> EndpointStateModel:
        if not await self.repository.get_by_id(state_id):
            raise HTTPException(status_code=404, detail="Endpoint state not found")
        updated = await self.repository.update(state_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update endpoint state")
        return updated

    async def delete_state(self, state_id: str) -> dict:
        if not await self.repository.get_by_id(state_id):
            raise HTTPException(status_code=404, detail="Endpoint state not found")
        success = await self.repository.delete(state_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete endpoint state")
        return {"detail": f"Endpoint state '{state_id}' deleted"}