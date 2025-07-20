import time as T
from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import EndpointModel, SecurityPolicyModel
from cryptomesh.repositories.base_repository import BaseRepository
from pymongo import ReturnDocument
from pymongo.errors import PyMongoError
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class EndpointsRepository(BaseRepository[EndpointModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, EndpointModel)

    async def update(self, endpoint_id: str, updates: dict) -> EndpointModel | None:
        t1 = T.time()
        try:
            sp = updates.get("security_policy")
            if sp and isinstance(sp, SecurityPolicyModel):
                updates["security_policy"] = sp.model_dump(by_alias=True, exclude_unset=True)

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
                return self.model(**updated)
            else:
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

    async def create(self, endpoint: EndpointModel) -> EndpointModel | None:
        t1 = T.time()
        try:
            data = endpoint.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

            sp = data.get("security_policy")
            if sp and isinstance(sp, SecurityPolicyModel):
                data["security_policy"] = sp.model_dump(by_alias=True, exclude_unset=True, exclude_none=True)

            result = await self.collection.insert_one(data)

            if result.inserted_id:
                L.debug({
                    "event": "REPO.ENDPOINT.CREATED",
                    "endpoint_id": endpoint.endpoint_id,
                    "time": round(T.time() - t1, 4)
                })
                return endpoint
            else:
                L.warning({
                    "event": "REPO.ENDPOINT.CREATE.NOT_INSERTED",
                    "endpoint_id": endpoint.endpoint_id,
                    "time": round(T.time() - t1, 4)
                })
                return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.ENDPOINT.CREATE.FAIL",
                "endpoint_id": endpoint.endpoint_id,
                "error": str(e)
            })
            return None


