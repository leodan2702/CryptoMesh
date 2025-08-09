# cryptomesh/repositories/endpoints_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import EndpointModel
from cryptomesh.repositories.base_repository import BaseRepository

class EndpointsRepository(BaseRepository[EndpointModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, EndpointModel)


