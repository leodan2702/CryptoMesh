from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from typing import List, Optional
from cryptomesh.models import FunctionStateModel

class FunctionStateRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, state: FunctionStateModel) -> Optional[FunctionStateModel]:
        try:
            state_dict = state.dict(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(state_dict)
            if result.inserted_id:
                return state
            return None
        except PyMongoError as e:
            print(f"❌ Error al crear function state: {e}")
            return None

    async def get_all(self) -> List[FunctionStateModel]:
        states = []
        cursor = self.collection.find({})
        async for document in cursor:
            states.append(FunctionStateModel(**document))
        return states

    async def get_by_id(self, state_id: str) -> Optional[FunctionStateModel]:
        document = await self.collection.find_one({"state_id": state_id})
        if document:
            return FunctionStateModel(**document)
        return None

    async def update(self, state_id: str, updates: dict) -> Optional[FunctionStateModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"state_id": state_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            if updated:
                return FunctionStateModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error al actualizar function state: {e}")
            return None

    async def delete(self, state_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"state_id": state_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error al eliminar function state: {e}")
            return False