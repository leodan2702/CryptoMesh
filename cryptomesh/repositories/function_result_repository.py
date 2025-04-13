from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from typing import List, Optional
from cryptomesh.models import FunctionResultModel

class FunctionResultRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, result: FunctionResultModel) -> Optional[FunctionResultModel]:
        try:
            result_dict = result.model_dump(by_alias=True, exclude_unset=True)
            res = await self.collection.insert_one(result_dict)
            if res.inserted_id:
                return result
            return None
        except PyMongoError as e:
            print(f"❌ Error al crear function result: {e}")
            return None

    async def get_all(self) -> List[FunctionResultModel]:
        results = []
        cursor = self.collection.find({})
        async for document in cursor:
            results.append(FunctionResultModel(**document))
        return results

    async def get_by_id(self, result_id: str) -> Optional[FunctionResultModel]:
        document = await self.collection.find_one({"state_id": result_id})
        if document:
            return FunctionResultModel(**document)
        return None

    async def update(self, result_id: str, updates: dict) -> Optional[FunctionResultModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"state_id": result_id},
                {"$set": updates},
                return_document=True
            )
            if updated:
                return FunctionResultModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error al actualizar function result: {e}")
            return None

    async def delete(self, result_id: str) -> bool:
        try:
            res = await self.collection.delete_one({"state_id": result_id})
            return res.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error al eliminar function result: {e}")
            return False