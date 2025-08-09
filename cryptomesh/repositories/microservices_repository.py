from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import MicroserviceModel
from cryptomesh.repositories.base_repository import BaseRepository

class MicroservicesRepository(BaseRepository[MicroserviceModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, MicroserviceModel)

