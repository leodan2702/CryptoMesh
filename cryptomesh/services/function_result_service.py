from fastapi import HTTPException
from typing import List
from cryptomesh.models import FunctionResultModel
from cryptomesh.repositories.function_result_repository import FunctionResultRepository

class FunctionResultService:
    def __init__(self, repository: FunctionResultRepository):
        self.repository = repository

    async def create_result(self, result: FunctionResultModel) -> FunctionResultModel:
        if await self.repository.get_by_id(result.state_id):
            raise HTTPException(status_code=400, detail="Function result already exists")
        created = await self.repository.create(result)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create function result")
        return created

    async def list_results(self) -> List[FunctionResultModel]:
        return await self.repository.get_all()

    async def get_result(self, result_id: str) -> FunctionResultModel:
        result = await self.repository.get_by_id(result_id)
        if not result:
            raise HTTPException(status_code=404, detail="Function result not found")
        return result

    async def update_result(self, result_id: str, updates: dict) -> FunctionResultModel:
        if not await self.repository.get_by_id(result_id):
            raise HTTPException(status_code=404, detail="Function result not found")
        updated = await self.repository.update(result_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update function result")
        return updated

    async def delete_result(self, result_id: str) -> dict:
        if not await self.repository.get_by_id(result_id):
            raise HTTPException(status_code=404, detail="Function result not found")
        success = await self.repository.delete(result_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete function result")
        return {"detail": f"Function result '{result_id}' deleted"}