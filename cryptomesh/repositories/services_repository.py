# cryptomesh/repositories/services_repository.py
import time as T
from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from cryptomesh.models import ServiceModel
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class ServicesRepository:
    """
    Repositorio encargado de gestionar el acceso a la colección 'services' en MongoDB.
    """

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, service: ServiceModel) -> Optional[ServiceModel]:
        t1 = T.time()
        try:
            service_dict = service.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(service_dict)
            elapsed = round(T.time() - t1, 4)
            if result.inserted_id:
                L.debug({
                    "event": "REPO.SERVICE.CREATED",
                    "service_id": service.service_id,
                    "time": elapsed
                })
                return service
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.SERVICE.CREATE.FAIL",
                "service_id": service.service_id,
                "error": str(e)
            })
            return None

    async def get_all(self) -> List[ServiceModel]:
        t1 = T.time()
        services = []
        try:
            cursor = self.collection.find({})
            async for document in cursor:
                services.append(ServiceModel(**document))
            elapsed = round(T.time() - t1, 4)
            L.debug({
                "event": "REPO.SERVICE.LISTED",
                "count": len(services),
                "time": elapsed
            })
            return services
        except PyMongoError as e:
            L.error({
                "event": "REPO.SERVICE.LIST.FAIL",
                "error": str(e)
            })
            return []

    async def get_by_id(self, service_id: str) -> Optional[ServiceModel]:
        t1 = T.time()
        try:
            document = await self.collection.find_one({"service_id": service_id})
            elapsed = round(T.time() - t1, 4)
            L.debug({
                "event": "REPO.SERVICE.FETCHED",
                "service_id": service_id,
                "found": document is not None,
                "time": elapsed
            })
            return ServiceModel(**document) if document else None
        except PyMongoError as e:
            L.error({
                "event": "REPO.SERVICE.FETCH.FAIL",
                "service_id": service_id,
                "error": str(e)
            })
            return None

    async def update(self, service_id: str, updates: dict) -> Optional[ServiceModel]:
        t1 = T.time()
        try:
            updated = await self.collection.find_one_and_update(
                {"service_id": service_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            elapsed = round(T.time() - t1, 4)
            if updated:
                L.debug({
                    "event": "REPO.SERVICE.UPDATED",
                    "service_id": service_id,
                    "updates": updates,
                    "time": elapsed
                })
                return ServiceModel(**updated)
            L.warning({
                "event": "REPO.SERVICE.UPDATE.NOT_FOUND",
                "service_id": service_id,
                "time": elapsed
            })
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.SERVICE.UPDATE.FAIL",
                "service_id": service_id,
                "error": str(e)
            })
            return None

    async def delete(self, service_id: str) -> bool:
        t1 = T.time()
        try:
            result = await self.collection.delete_one({"service_id": service_id})
            elapsed = round(T.time() - t1, 4)
            success = result.deleted_count > 0
            L.debug({
                "event": "REPO.SERVICE.DELETED",
                "service_id": service_id,
                "success": success,
                "time": elapsed
            })
            return success
        except PyMongoError as e:
            L.error({
                "event": "REPO.SERVICE.DELETE.FAIL",
                "service_id": service_id,
                "error": str(e)
            })
            return False

