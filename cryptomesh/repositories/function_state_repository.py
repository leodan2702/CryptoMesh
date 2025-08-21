from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import FunctionStateModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class FunctionStateRepository(BaseRepository[FunctionStateModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, FunctionStateModel)

    async def get_by_id(self, state_id: str, id_field: str = "state_id") -> Optional[FunctionStateModel]:
        document = await self.collection.find_one({"state_id": state_id})
        return FunctionStateModel(**document) if document else None