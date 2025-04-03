from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import FunctionModel


class FunctionsRepository():
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_all(self) -> list[FunctionModel]:
        functions = []
        cursor = self.collection.find({})
        async for document in cursor:
            functions.append(FunctionModel(**document))
        return functions
