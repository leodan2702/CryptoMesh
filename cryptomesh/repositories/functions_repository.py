# cryptomesh/repositories/functions_repository.py
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from typing import List, Optional
from cryptomesh.models import FunctionModel

class FunctionsRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, function: FunctionModel) -> Optional[FunctionModel]:
        try:
            function_dict = function.dict(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(function_dict)
            if result.inserted_id:
                return function
            return None
        except PyMongoError as e:
            print(f"❌ Error al crear función: {e}")
            return None

    async def get_all(self) -> List[FunctionModel]:
        functions = []
        cursor = self.collection.find({})
        async for document in cursor:
            functions.append(FunctionModel(**document))
        return functions

    async def get_by_id(self, function_id: str) -> Optional[FunctionModel]:
        document = await self.collection.find_one({"function_id": function_id})
        if document:
            return FunctionModel(**document)
        return None

    async def update(self, function_id: str, updates: dict) -> Optional[FunctionModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"function_id": function_id},
                {"$set": updates},
                return_document=True
            )
            if updated:
                return FunctionModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error al actualizar función: {e}")
            return None

    async def delete(self, function_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"function_id": function_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error al eliminar función: {e}")
            return False
