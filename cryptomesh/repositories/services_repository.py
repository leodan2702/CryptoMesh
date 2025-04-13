from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Optional
from pymongo.errors import PyMongoError
from cryptomesh.models import ServiceModel

class ServicesRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, service: ServiceModel) -> Optional[ServiceModel]:
        try:
            service_dict = service.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(service_dict)
            if result.inserted_id:
                return service
            return None
        except PyMongoError as e:
            print(f"❌ Error al crear service: {e}")
            return None

    async def get_all(self) -> List[ServiceModel]:
        services = []
        cursor = self.collection.find({})
        async for document in cursor:
            services.append(ServiceModel(**document))
        return services

    async def get_by_id(self, service_id: str) -> Optional[ServiceModel]:
        document = await self.collection.find_one({"service_id": service_id})
        if document:
            return ServiceModel(**document)
        return None

    async def update(self, service_id: str, updates: dict) -> Optional[ServiceModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"service_id": service_id},
                {"$set": updates},
                return_document=True
            )
            if updated:
                return ServiceModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error al actualizar service: {e}")
            return None

    async def delete(self, service_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"service_id": service_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error al eliminar service: {e}")
            return False
