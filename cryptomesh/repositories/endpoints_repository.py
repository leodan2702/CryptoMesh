# cryptomesh/repositories/endpoints_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import EndpointModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class EndpointsRepository(BaseRepository[EndpointModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, EndpointModel)

    async def get_by_id(self, endpoint_id: str, id_field: str = "endpoint_id") -> Optional[EndpointModel]:
        document = await self.collection.find_one({"endpoint_id": endpoint_id})
        return EndpointModel(**document) if document else None



