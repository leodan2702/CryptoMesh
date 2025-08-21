from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import MicroserviceModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class MicroservicesRepository(BaseRepository[MicroserviceModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, MicroserviceModel)

    async def get_by_id(self, microservice_id: str, id_field: str = "microservice_id") -> Optional[MicroserviceModel]:
        document = await self.collection.find_one({"microservice_id": microservice_id})
        return MicroserviceModel(**document) if document else None

