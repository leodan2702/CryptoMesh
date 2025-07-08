import time as T
from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Optional
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from cryptomesh.models import MicroserviceModel
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class MicroservicesRepository:
    """
    Repositorio encargado de gestionar la colección 'microservices' en MongoDB.
    """

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, microservice: MicroserviceModel) -> Optional[MicroserviceModel]:
        t1 = T.time()
        try:
            microservice_dict = microservice.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(microservice_dict)
            elapsed = round(T.time() - t1, 4)
            if result.inserted_id:
                L.debug({
                    "event": "REPO.MICROSERVICE.CREATED",
                    "microservice_id": microservice.microservice_id,
                    "time": elapsed
                })
                return microservice
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.MICROSERVICE.CREATE.FAIL",
                "microservice_id": microservice.microservice_id,
                "error": str(e)
            })
            return None

    async def get_all(self) -> List[MicroserviceModel]:
        t1 = T.time()
        try:
            microservices = []
            cursor = self.collection.find({})
            async for document in cursor:
                microservices.append(MicroserviceModel(**document))
            elapsed = round(T.time() - t1, 4)
            L.debug({
                "event": "REPO.MICROSERVICE.LISTED",
                "count": len(microservices),
                "time": elapsed
            })
            return microservices
        except PyMongoError as e:
            L.error({
                "event": "REPO.MICROSERVICE.LIST.FAIL",
                "error": str(e)
            })
            return []

    async def get_by_id(self, microservice_id: str) -> Optional[MicroserviceModel]:
        t1 = T.time()
        try:
            document = await self.collection.find_one({"microservice_id": microservice_id})
            elapsed = round(T.time() - t1, 4)
            L.debug({
                "event": "REPO.MICROSERVICE.FETCHED",
                "microservice_id": microservice_id,
                "found": document is not None,
                "time": elapsed
            })
            return MicroserviceModel(**document) if document else None
        except PyMongoError as e:
            L.error({
                "event": "REPO.MICROSERVICE.FETCH.FAIL",
                "microservice_id": microservice_id,
                "error": str(e)
            })
            return None

    async def update(self, microservice_id: str, updates: dict) -> Optional[MicroserviceModel]:
        t1 = T.time()
        try:
            updated = await self.collection.find_one_and_update(
                {"microservice_id": microservice_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            elapsed = round(T.time() - t1, 4)
            if updated:
                L.debug({
                    "event": "REPO.MICROSERVICE.UPDATED",
                    "microservice_id": microservice_id,
                    "updates": updates,
                    "time": elapsed
                })
                return MicroserviceModel(**updated)
            else:
                L.warning({
                    "event": "REPO.MICROSERVICE.UPDATE.NOT_MODIFIED",
                    "microservice_id": microservice_id,
                    "time": elapsed
                })
                return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.MICROSERVICE.UPDATE.FAIL",
                "microservice_id": microservice_id,
                "error": str(e)
            })
            return None

    async def delete(self, microservice_id: str) -> bool:
        t1 = T.time()
        try:
            result = await self.collection.delete_one({"microservice_id": microservice_id})
            elapsed = round(T.time() - t1, 4)
            success = result.deleted_count > 0
            L.debug({
                "event": "REPO.MICROSERVICE.DELETED",
                "microservice_id": microservice_id,
                "success": success,
                "time": elapsed
            })
            return success
        except PyMongoError as e:
            L.error({
                "event": "REPO.MICROSERVICE.DELETE.FAIL",
                "microservice_id": microservice_id,
                "error": str(e)
            })
            return False

