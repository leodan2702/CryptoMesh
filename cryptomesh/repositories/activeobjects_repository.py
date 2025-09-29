from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import ActiveObjectModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional, List

class ActiveObjectsRepository(BaseRepository):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, ActiveObjectModel)

    async def get_by_id(self, active_object_id: str, id_field: str = "active_object_id")-> Optional[ActiveObjectModel]:
        document = await self.collection.find_one({"active_object_id": active_object_id})
        return ActiveObjectModel(**document) if document else None

    async def get_by_filter(self, filter: dict)-> List[ActiveObjectModel]:
        docs = []
        cursor = self.collection.find(filter)
        async for doc in cursor:
            docs.append(ActiveObjectModel(**doc))
        return docs