# cryptomesh/repositories/endpoints_repository.py
import time as T
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from typing import List, Optional
from cryptomesh.models import EndpointModel
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class EndpointsRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, endpoint: EndpointModel) -> Optional[EndpointModel]:
        t1 = T.time()
        try:
            endpoint_dict = endpoint.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(endpoint_dict)
            if result.inserted_id:
                L.debug({
                    "event": "REPO.ENDPOINT.CREATED",
                    "endpoint_id": endpoint.endpoint_id,
                    "time": round(T.time() - t1, 4)
                })
                return endpoint
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.ENDPOINT.CREATE.FAIL",
                "endpoint_id": endpoint.endpoint_id,
                "error": str(e)
            })
            return None

    async def get_all(self) -> List[EndpointModel]:
        t1 = T.time()
        try:
            endpoints = []
            cursor = self.collection.find({})
            async for document in cursor:
                endpoints.append(EndpointModel(**document))
            L.debug({
                "event": "REPO.ENDPOINT.LISTED",
                "count": len(endpoints),
                "time": round(T.time() - t1, 4)
            })
            return endpoints
        except PyMongoError as e:
            L.error({
                "event": "REPO.ENDPOINT.LIST.FAIL",
                "error": str(e)
            })
            return []

    async def get_by_id(self, endpoint_id: str) -> Optional[EndpointModel]:
        t1 = T.time()
        try:
            document = await self.collection.find_one({"endpoint_id": endpoint_id})
            L.debug({
                "event": "REPO.ENDPOINT.FETCHED",
                "endpoint_id": endpoint_id,
                "found": document is not None,
                "time": round(T.time() - t1, 4)
            })
            if document:
                return EndpointModel(**document)
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.ENDPOINT.FETCH.FAIL",
                "endpoint_id": endpoint_id,
                "error": str(e)
            })
            return None

    async def update(self, endpoint_id: str, updates: dict) -> Optional[EndpointModel]:
        t1 = T.time()
        try:
            updated = await self.collection.find_one_and_update(
                {"endpoint_id": endpoint_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            if updated:
                L.debug({
                    "event": "REPO.ENDPOINT.UPDATED",
                    "endpoint_id": endpoint_id,
                    "updates": updates,
                    "time": round(T.time() - t1, 4)
                })
                return EndpointModel(**updated)
            L.warning({
                "event": "REPO.ENDPOINT.UPDATE.NOT_MODIFIED",
                "endpoint_id": endpoint_id,
                "time": round(T.time() - t1, 4)
            })
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.ENDPOINT.UPDATE.FAIL",
                "endpoint_id": endpoint_id,
                "error": str(e)
            })
            return None

    async def delete(self, endpoint_id: str) -> bool:
        t1 = T.time()
        try:
            result = await self.collection.delete_one({"endpoint_id": endpoint_id})
            success = result.deleted_count > 0
            L.debug({
                "event": "REPO.ENDPOINT.DELETED",
                "endpoint_id": endpoint_id,
                "success": success,
                "time": round(T.time() - t1, 4)
            })
            return success
        except PyMongoError as e:
            L.error({
                "event": "REPO.ENDPOINT.DELETE.FAIL",
                "endpoint_id": endpoint_id,
                "error": str(e)
            })
            return False


