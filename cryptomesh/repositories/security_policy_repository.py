import time as T
from typing import Optional, List
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class SecurityPolicyRepository:
    """
    Repositorio encargado de gestionar el acceso a la colección 'security_policies' en MongoDB.
    """

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, policy: SecurityPolicyModel) -> Optional[SecurityPolicyModel]:
        t1 = T.time()
        try:
            policy_dict = policy.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(policy_dict)
            elapsed = round(T.time() - t1, 4)
            if result.inserted_id:
                L.debug({
                    "event": "REPO.SECURITY_POLICY.CREATED",
                    "sp_id": policy.sp_id,
                    "time": elapsed
                })
                return policy
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.SECURITY_POLICY.CREATE.FAIL",
                "sp_id": policy.sp_id,
                "error": str(e)
            })
            return None

    async def get_all(self) -> List[SecurityPolicyModel]:
        t1 = T.time()
        policies = []
        try:
            cursor = self.collection.find({})
            async for document in cursor:
                policies.append(SecurityPolicyModel(**document))
            elapsed = round(T.time() - t1, 4)
            L.debug({
                "event": "REPO.SECURITY_POLICY.LISTED",
                "count": len(policies),
                "time": elapsed
            })
            return policies
        except PyMongoError as e:
            L.error({
                "event": "REPO.SECURITY_POLICY.LIST.FAIL",
                "error": str(e)
            })
            return []

    async def get_by_id(self, sp_id: str) -> Optional[SecurityPolicyModel]:
        t1 = T.time()
        try:
            document = await self.collection.find_one({"sp_id": sp_id})
            elapsed = round(T.time() - t1, 4)
            L.debug({
                "event": "REPO.SECURITY_POLICY.FETCHED",
                "sp_id": sp_id,
                "found": document is not None,
                "time": elapsed
            })
            return SecurityPolicyModel(**document) if document else None
        except PyMongoError as e:
            L.error({
                "event": "REPO.SECURITY_POLICY.FETCH.FAIL",
                "sp_id": sp_id,
                "error": str(e)
            })
            return None

    async def update(self, sp_id: str, updates: dict) -> Optional[SecurityPolicyModel]:
        t1 = T.time()
        try:
            updated = await self.collection.find_one_and_update(
                {"sp_id": sp_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            elapsed = round(T.time() - t1, 4)
            if updated:
                L.debug({
                    "event": "REPO.SECURITY_POLICY.UPDATED",
                    "sp_id": sp_id,
                    "updates": updates,
                    "time": elapsed
                })
                return SecurityPolicyModel(**updated)
            L.warning({
                "event": "REPO.SECURITY_POLICY.UPDATE.NOT_FOUND",
                "sp_id": sp_id,
                "time": elapsed
            })
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.SECURITY_POLICY.UPDATE.FAIL",
                "sp_id": sp_id,
                "error": str(e)
            })
            return None

    async def delete(self, sp_id: str) -> bool:
        t1 = T.time()
        try:
            result = await self.collection.delete_one({"sp_id": sp_id})
            elapsed = round(T.time() - t1, 4)
            success = result.deleted_count > 0
            L.debug({
                "event": "REPO.SECURITY_POLICY.DELETED",
                "sp_id": sp_id,
                "success": success,
                "time": elapsed
            })
            return success
        except PyMongoError as e:
            L.error({
                "event": "REPO.SECURITY_POLICY.DELETE.FAIL",
                "sp_id": sp_id,
                "error": str(e)
            })
            return False


