import time as T
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from typing import List, Optional
from cryptomesh.models import FunctionStateModel
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class FunctionStateRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, state: FunctionStateModel) -> Optional[FunctionStateModel]:
        t1 = T.time()
        try:
            state_dict = state.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(state_dict)
            if result.inserted_id:
                L.debug({
                    "event": "REPO.FUNCTION_STATE.CREATED",
                    "state_id": state.state_id,
                    "time": round(T.time() - t1, 4)
                })
                return state
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_STATE.CREATE.FAIL",
                "state_id": state.state_id,
                "error": str(e)
            })
            return None

    async def get_all(self) -> List[FunctionStateModel]:
        t1 = T.time()
        try:
            states = []
            cursor = self.collection.find({})
            async for document in cursor:
                states.append(FunctionStateModel(**document))
            L.debug({
                "event": "REPO.FUNCTION_STATE.LISTED",
                "count": len(states),
                "time": round(T.time() - t1, 4)
            })
            return states
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_STATE.LIST.FAIL",
                "error": str(e)
            })
            return []

    async def get_by_id(self, state_id: str) -> Optional[FunctionStateModel]:
        t1 = T.time()
        try:
            document = await self.collection.find_one({"state_id": state_id})
            L.debug({
                "event": "REPO.FUNCTION_STATE.FETCHED",
                "state_id": state_id,
                "found": document is not None,
                "time": round(T.time() - t1, 4)
            })
            if document:
                return FunctionStateModel(**document)
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_STATE.FETCH.FAIL",
                "state_id": state_id,
                "error": str(e)
            })
            return None

    async def update(self, state_id: str, updates: dict) -> Optional[FunctionStateModel]:
        t1 = T.time()
        try:
            updated = await self.collection.find_one_and_update(
                {"state_id": state_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            if updated:
                L.debug({
                    "event": "REPO.FUNCTION_STATE.UPDATED",
                    "state_id": state_id,
                    "updates": updates,
                    "time": round(T.time() - t1, 4)
                })
                return FunctionStateModel(**updated)
            L.warning({
                "event": "REPO.FUNCTION_STATE.UPDATE.NOT_MODIFIED",
                "state_id": state_id,
                "time": round(T.time() - t1, 4)
            })
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_STATE.UPDATE.FAIL",
                "state_id": state_id,
                "error": str(e)
            })
            return None

    async def delete(self, state_id: str) -> bool:
        t1 = T.time()
        try:
            result = await self.collection.delete_one({"state_id": state_id})
            success = result.deleted_count > 0
            L.debug({
                "event": "REPO.FUNCTION_STATE.DELETED",
                "state_id": state_id,
                "success": success,
                "time": round(T.time() - t1, 4)
            })
            return success
        except PyMongoError as e:
            L.error({
                "event": "REPO.FUNCTION_STATE.DELETE.FAIL",
                "state_id": state_id,
                "error": str(e)
            })
            return False
