from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import FunctionResultModel
from cryptomesh.repositories.base_repository import BaseRepository

class FunctionResultRepository(BaseRepository[FunctionResultModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, FunctionResultModel)

