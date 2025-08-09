from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import FunctionModel
from cryptomesh.repositories.base_repository import BaseRepository

class FunctionsRepository(BaseRepository[FunctionModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, FunctionModel)
