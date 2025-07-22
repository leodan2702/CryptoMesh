from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import FunctionStateModel
from cryptomesh.repositories.base_repository import BaseRepository

class FunctionStateRepository(BaseRepository[FunctionStateModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, FunctionStateModel)
