# cryptomesh/services/functions_services.py
from fastapi import HTTPException
from cryptomesh.models import FunctionModel
from cryptomesh.repositories.functions_repository import FunctionsRepository

class FunctionsService:
    def __init__(self, repository: FunctionsRepository):
        self.repository = repository

    async def create_function(self, data: FunctionModel):
        if await self.repository.get_by_id(data.function_id):
            raise HTTPException(status_code=400, detail="Function already exists")
        function = await self.repository.create(data)
        if not function:
            raise HTTPException(status_code=500, detail="Failed to create function")
        return function

    async def list_functions(self):
        return await self.repository.get_all()

    async def get_function(self, function_id: str):
        function = await self.repository.get_by_id(function_id)
        if not function:
            raise HTTPException(status_code=404, detail="Function not found")
        return function

    async def update_function(self, function_id: str, updates: dict):
        if not await self.repository.get_by_id(function_id):
            raise HTTPException(status_code=404, detail="Function not found")
        updated = await self.repository.update(function_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update function")
        return updated

    async def delete_function(self, function_id: str):
        if not await self.repository.get_by_id(function_id):
            raise HTTPException(status_code=404, detail="Function not found")
        success = await self.repository.delete(function_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete function")
        return {"detail": f"Function '{function_id}' deleted"}

