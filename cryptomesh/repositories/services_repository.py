from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import ServiceModel
from cryptomesh.repositories.base_repository import BaseRepository

class ServicesRepository(BaseRepository[ServiceModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, ServiceModel)
