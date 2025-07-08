import time as T
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from typing import List, Optional
from cryptomesh.models import FunctionResultModel
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class FunctionResultRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, result: FunctionResultModel) -> Optional[FunctionResultModel]:
        t1 = T.time()
        try:
            result_dict = result.model_dump(by_alias=True, exclude_unset=True)
            res = await self.collection.insert_one(result_dict)
            if res.inserted_id:
                L.debug({
                    "event": "REPO.FUNCTION_RESULT.CREATED",
                    "state_id": result.state_id,
                    "time": round(T.time() - t1, 4)
                })
                return result
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_RESULT.CREATE.FAIL",
                "state_id": result.state_id,
                "error": str(e)
            })
            return None

    async def get_all(self) -> List[FunctionResultModel]:
        t1 = T.time()
        try:
            results = []
            cursor = self.collection.find({})
            async for document in cursor:
                results.append(FunctionResultModel(**document))
            L.debug({
                "event": "REPO.FUNCTION_RESULT.LISTED",
                "count": len(results),
                "time": round(T.time() - t1, 4)
            })
            return results
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_RESULT.LIST.FAIL",
                "error": str(e)
            })
            return []

    async def get_by_id(self, result_id: str) -> Optional[FunctionResultModel]:
        t1 = T.time()
        try:
            document = await self.collection.find_one({"state_id": result_id})
            L.debug({
                "event": "REPO.FUNCTION_RESULT.FETCHED",
                "state_id": result_id,
                "found": document is not None,
                "time": round(T.time() - t1, 4)
            })
            if document:
                return FunctionResultModel(**document)
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_RESULT.FETCH.FAIL",
                "state_id": result_id,
                "error": str(e)
            })
            return None

    async def update(self, result_id: str, updates: dict) -> Optional[FunctionResultModel]:
        t1 = T.time()
        try:
            updated = await self.collection.find_one_and_update(
                {"state_id": result_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            if updated:
                L.debug({
                    "event": "REPO.FUNCTION_RESULT.UPDATED",
                    "state_id": result_id,
                    "updates": updates,
                    "time": round(T.time() - t1, 4)
                })
                return FunctionResultModel(**updated)
            L.warning({
                "event": "REPO.FUNCTION_RESULT.UPDATE.NOT_MODIFIED",
                "state_id": result_id,
                "time": round(T.time() - t1, 4)
            })
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_RESULT.UPDATE.FAIL",
                "state_id": result_id,
                "error": str(e)
            })
            return None

    async def delete(self, result_id: str) -> bool:
        t1 = T.time()
        try:
            res = await self.collection.delete_one({"state_id": result_id})
            success = res.deleted_count > 0
            L.debug({
                "event": "REPO.FUNCTION_RESULT.DELETED",
                "state_id": result_id,
                "success": success,
                "time": round(T.time() - t1, 4)
            })
            return success
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_RESULT.DELETE.FAIL",
                "state_id": result_id,
                "error": str(e)
            })
            return False
