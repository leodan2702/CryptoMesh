import time as T
from typing import Any
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError
from cryptomesh.models import ServiceModel, SecurityPolicyModel
from cryptomesh.repositories.base_repository import BaseRepository
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class ServicesRepository(BaseRepository[ServiceModel]):
    """
    Repositorio encargado de gestionar el acceso a la colección 'services' en MongoDB.
    """

    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, ServiceModel)

    async def create(self, service: ServiceModel) -> ServiceModel | None:
        t1 = T.time()
        try:
            data = service.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

            sp = data.get("security_policy")
            if sp and isinstance(sp, SecurityPolicyModel):
                data["security_policy"] = sp.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

            result = await self.collection.insert_one(data)

            if result.inserted_id:
                L.debug({
                    "event": "REPO.SERVICE.CREATED",
                    "service_id": service.service_id,
                    "time": round(T.time() - t1, 4)
                })
                return service
            else:
                L.warning({
                    "event": "REPO.SERVICE.CREATE.NOT_INSERTED",
                    "service_id": service.service_id,
                    "time": round(T.time() - t1, 4)
                })
                return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.SERVICE.CREATE.FAIL",
                "service_id": service.service_id,
                "error": str(e)
            })
            return None

    async def update(self, service_id: str, updates: dict[str, Any]) -> ServiceModel | None:
        t1 = T.time()
        try:
            sp = updates.get("security_policy")
            if sp and isinstance(sp, SecurityPolicyModel):
                updates["security_policy"] = sp.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

            updated = await self.collection.find_one_and_update(
                {"service_id": service_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )

            if updated:
                L.debug({
                    "event": "REPO.SERVICE.UPDATED",
                    "service_id": service_id,
                    "updates": updates,
                    "time": round(T.time() - t1, 4)
                })
                return self.model(**updated)
            else:
                L.warning({
                    "event": "REPO.SERVICE.UPDATE.NOT_MODIFIED",
                    "service_id": service_id,
                    "time": round(T.time() - t1, 4)
                })
                return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.SERVICE.UPDATE.FAIL",
                "service_id": service_id,
                "error": str(e)
            })
            return None


