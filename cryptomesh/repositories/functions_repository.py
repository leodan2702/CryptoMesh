from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import FunctionModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class FunctionsRepository(BaseRepository[FunctionModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, FunctionModel)

    async def get_by_id(self, function_id: str, id_field: str = "function_id") -> Optional[FunctionModel]:
        document = await self.collection.find_one({"function_id": function_id})
        return FunctionModel(**document) if document else None
