# cryptomesh/repositories/endpoint_state_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import EndpointStateModel
from cryptomesh.repositories.base_repository import BaseRepository

class EndpointStateRepository(BaseRepository[EndpointStateModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, EndpointStateModel)
