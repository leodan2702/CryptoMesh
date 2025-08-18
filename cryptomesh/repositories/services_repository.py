from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import ServiceModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class ServicesRepository(BaseRepository[ServiceModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, ServiceModel)

    async def get_by_id(self, service_id: str, id_field: str = "service_id") -> Optional[ServiceModel]:
        document = await self.collection.find_one({"service_id": service_id})
        return ServiceModel(**document) if document else None
