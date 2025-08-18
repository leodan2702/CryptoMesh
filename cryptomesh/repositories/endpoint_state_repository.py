# cryptomesh/repositories/endpoint_state_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import EndpointStateModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class EndpointStateRepository(BaseRepository[EndpointStateModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, EndpointStateModel)

    async def get_by_id(self, state_id: str, id_field: str = "state_id") -> Optional[EndpointStateModel]:
        document = await self.collection.find_one({"state_id": state_id})
        return EndpointStateModel(**document) if document else None
