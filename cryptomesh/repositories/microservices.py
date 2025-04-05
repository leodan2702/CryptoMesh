from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import MicroserviceModel


class MicroservicesRepository():
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def find_all(self) -> list[MicroserviceModel]:
        microservices = []
        cursor = self.collection.find({})
        async for document in cursor:
            microservices.append(MicroserviceModel(**document))
        return microservices
