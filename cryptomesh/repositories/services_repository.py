from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import ServiceModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class ServicesRepository(BaseRepository[ServiceModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, ServiceModel)

    async def get_by_id(self, service_id: str, id_field: str = "service_id") -> Optional[ServiceModel]:
        document = await self.collection.find_one({id_field: service_id})
        return ServiceModel(**document) if document else None

    async def update_push_microservice(self, service_id: str, microservice_id: str):
        result = await self.collection.update_one(
            {"service_id": service_id},
            {"$addToSet": {"microservices": microservice_id}}
        )
        return result

    async def update_pull_microservice(self, service_id: str, microservice_id: str):
        result = await self.collection.update_one(
            {"service_id": service_id},
            {"$pull": {"microservices": microservice_id}}
        )
        return result

