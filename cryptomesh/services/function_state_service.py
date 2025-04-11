from fastapi import HTTPException
from typing import List
from cryptomesh.models import FunctionStateModel
from cryptomesh.repositories.function_state_repository import FunctionStateRepository

class FunctionStateService:
    def __init__(self, repository: FunctionStateRepository):
        self.repository = repository

    async def create_state(self, state: FunctionStateModel) -> FunctionStateModel:
        if await self.repository.get_by_id(state.state_id):
            raise HTTPException(status_code=400, detail="Function state already exists")
        created = await self.repository.create(state)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create function state")
        return created

    async def list_states(self) -> List[FunctionStateModel]:
        return await self.repository.get_all()

    async def get_state(self, state_id: str) -> FunctionStateModel:
        state = await self.repository.get_by_id(state_id)
        if not state:
            raise HTTPException(status_code=404, detail="Function state not found")
        return state

    async def update_state(self, state_id: str, updates: dict) -> FunctionStateModel:
        if not await self.repository.get_by_id(state_id):
            raise HTTPException(status_code=404, detail="Function state not found")
        updated = await self.repository.update(state_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update function state")
        return updated

    async def delete_state(self, state_id: str) -> dict:
        if not await self.repository.get_by_id(state_id):
            raise HTTPException(status_code=404, detail="Function state not found")
        success = await self.repository.delete(state_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete function state")
        return {"detail": f"Function state '{state_id}' deleted"}