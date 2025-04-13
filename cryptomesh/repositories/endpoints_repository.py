# cryptomesh/repositories/endpoints_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from typing import List, Optional
from cryptomesh.models import EndpointModel

class EndpointsRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, endpoint: EndpointModel) -> Optional[EndpointModel]:
        try:
            endpoint_dict = endpoint.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(endpoint_dict)
            if result.inserted_id:
                return endpoint
            return None
        except PyMongoError as e:
            print(f"❌ Error creating endpoint: {e}")
            return None

    async def get_all(self) -> List[EndpointModel]:
        endpoints = []
        cursor = self.collection.find({})
        async for document in cursor:
            endpoints.append(EndpointModel(**document))
        return endpoints

    async def get_by_id(self, endpoint_id: str) -> Optional[EndpointModel]:
        document = await self.collection.find_one({"endpoint_id": endpoint_id})
        if document:
            return EndpointModel(**document)
        return None

    async def update(self, endpoint_id: str, updates: dict) -> Optional[EndpointModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"endpoint_id": endpoint_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            if updated:
                return EndpointModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error updating endpoint: {e}")
            return None

    async def delete(self, endpoint_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"endpoint_id": endpoint_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error deleting endpoint: {e}")
            return False

