from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import FunctionResultModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class FunctionResultRepository(BaseRepository[FunctionResultModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, FunctionResultModel)

    async def get_by_id(self, result_id: str, id_field: str = "result_id") -> Optional[FunctionResultModel]:
        document = await self.collection.find_one({"result_id": result_id})
        return FunctionResultModel(**document) if document else None


