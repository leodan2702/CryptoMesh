import time as T
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError
from typing import List, Optional
from cryptomesh.models import FunctionModel
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class FunctionsRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, function: FunctionModel) -> Optional[FunctionModel]:
        t1 = T.time()
        try:
            function_dict = function.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(function_dict)
            if result.inserted_id:
                L.debug({
                    "event": "REPO.FUNCTION.CREATED",
                    "function_id": function.function_id,
                    "time": round(T.time() - t1, 4)
                })
                return function
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION.CREATE.FAIL",
                "function_id": function.function_id,
                "error": str(e)
            })
            return None

    async def get_all(self) -> List[FunctionModel]:
        t1 = T.time()
        try:
            functions = []
            cursor = self.collection.find({})
            async for document in cursor:
                functions.append(FunctionModel(**document))
            L.debug({
                "event": "REPO.FUNCTION.LISTED",
                "count": len(functions),
                "time": round(T.time() - t1, 4)
            })
            return functions
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION.LIST.FAIL",
                "error": str(e)
            })
            return []

    async def get_by_id(self, function_id: str) -> Optional[FunctionModel]:
        t1 = T.time()
        try:
            document = await self.collection.find_one({"function_id": function_id})
            L.debug({
                "event": "REPO.FUNCTION.FETCHED",
                "function_id": function_id,
                "found": document is not None,
                "time": round(T.time() - t1, 4)
            })
            if document:
                return FunctionModel(**document)
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION.FETCH.FAIL",
                "function_id": function_id,
                "error": str(e)
            })
            return None

    async def update(self, function_id: str, updates: dict) -> Optional[FunctionModel]:
        t1 = T.time()
        try:
            updated = await self.collection.find_one_and_update(
                {"function_id": function_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            if updated:
                L.debug({
                    "event": "REPO.FUNCTION.UPDATED",
                    "function_id": function_id,
                    "updates": updates,
                    "time": round(T.time() - t1, 4)
                })
                return FunctionModel(**updated)
            L.warning({
                "event": "REPO.FUNCTION.UPDATE.NOT_MODIFIED",
                "function_id": function_id,
                "time": round(T.time() - t1, 4)
            })
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION.UPDATE.FAIL",
                "function_id": function_id,
                "error": str(e)
            })
            return None

    async def delete(self, function_id: str) -> bool:
        t1 = T.time()
        try:
            result = await self.collection.delete_one({"function_id": function_id})
            success = result.deleted_count > 0
            L.debug({
                "event": "REPO.FUNCTION.DELETED",
                "function_id": function_id,
                "success": success,
                "time": round(T.time() - t1, 4)
            })
            return success
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION.DELETE.FAIL",
                "function_id": function_id,
                "error": str(e)
            })
            return False

