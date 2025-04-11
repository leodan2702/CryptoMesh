from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from typing import List, Optional
from cryptomesh.models import EndpointStateModel

class EndpointStateRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, state: EndpointStateModel) -> Optional[EndpointStateModel]:
        try:
            state_dict = state.dict(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(state_dict)
            if result.inserted_id:
                return state
            return None
        except PyMongoError as e:
            print(f"❌ Error creating endpoint state: {e}")
            return None

    async def get_all(self) -> List[EndpointStateModel]:
        states = []
        cursor = self.collection.find({})
        async for document in cursor:
            states.append(EndpointStateModel(**document))
        return states

    async def get_by_id(self, state_id: str) -> Optional[EndpointStateModel]:
        document = await self.collection.find_one({"state_id": state_id})
        if document:
            return EndpointStateModel(**document)
        return None

    async def update(self, state_id: str, updates: dict) -> Optional[EndpointStateModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"state_id": state_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            if updated:
                return EndpointStateModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error updating endpoint state: {e}")
            return None

    async def delete(self, state_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"state_id": state_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error deleting endpoint state: {e}")
            return False