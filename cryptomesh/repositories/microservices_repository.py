from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Optional
from pymongo.errors import PyMongoError
from cryptomesh.models import MicroserviceModel

class MicroservicesRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, microservice: MicroserviceModel) -> Optional[MicroserviceModel]:
        try:
            microservice_dict = microservice.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(microservice_dict)
            if result.inserted_id:
                return microservice
            return None
        except PyMongoError as e:
            print(f"❌ Error al crear microservicio: {e}")
            return None

    async def get_all(self) -> List[MicroserviceModel]:
        microservices = []
        cursor = self.collection.find({})
        async for document in cursor:
            microservices.append(MicroserviceModel(**document))
        return microservices

    async def get_by_id(self, microservice_id: str) -> Optional[MicroserviceModel]:
        document = await self.collection.find_one({"microservice_id": microservice_id})
        if document:
            return MicroserviceModel(**document)
        return None

    async def update(self, microservice_id: str, updates: dict) -> Optional[MicroserviceModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"microservice_id": microservice_id},
                {"$set": updates},
                return_document=True
            )
            if updated:
                return MicroserviceModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error al actualizar microservicio: {e}")
            return None

    async def delete(self, microservice_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"microservice_id": microservice_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error al eliminar microservicio:  {e}")
            return False

