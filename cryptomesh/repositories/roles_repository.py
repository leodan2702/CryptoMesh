import time as T
from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from typing import List, Optional
from cryptomesh.models import RoleModel
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class RolesRepository:
    """
    Repositorio encargado de gestionar la colección 'roles' en MongoDB.
    """

    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, role: RoleModel) -> Optional[RoleModel]:
        t1 = T.time()
        try:
            role_dict = role.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(role_dict)
            elapsed = round(T.time() - t1, 4)
            if result.inserted_id:
                L.debug({
                    "event": "REPO.ROLE.CREATED",
                    "role_id": role.role_id,
                    "time": elapsed
                })
                return role
            return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.ROLE.CREATE.FAIL",
                "role_id": role.role_id,
                "error": str(e)
            })
            return None

    async def get_all(self) -> List[RoleModel]:
        t1 = T.time()
        try:
            roles = []
            cursor = self.collection.find({})
            async for document in cursor:
                roles.append(RoleModel(**document))
            elapsed = round(T.time() - t1, 4)
            L.debug({
                "event": "REPO.ROLE.LISTED",
                "count": len(roles),
                "time": elapsed
            })
            return roles
        except PyMongoError as e:
            L.error({
                "event": "REPO.ROLE.LIST.FAIL",
                "error": str(e)
            })
            return []

    async def get_by_id(self, role_id: str) -> Optional[RoleModel]:
        t1 = T.time()
        try:
            document = await self.collection.find_one({"role_id": role_id})
            elapsed = round(T.time() - t1, 4)
            L.debug({
                "event": "REPO.ROLE.FETCHED",
                "role_id": role_id,
                "found": document is not None,
                "time": elapsed
            })
            return RoleModel(**document) if document else None
        except PyMongoError as e:
            L.error({
                "event": "REPO.ROLE.FETCH.FAIL",
                "role_id": role_id,
                "error": str(e)
            })
            return None

    async def update(self, role_id: str, updates: dict) -> Optional[RoleModel]:
        t1 = T.time()
        try:
            updated = await self.collection.find_one_and_update(
                {"role_id": role_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            elapsed = round(T.time() - t1, 4)
            if updated:
                L.debug({
                    "event": "REPO.ROLE.UPDATED",
                    "role_id": role_id,
                    "updates": updates,
                    "time": elapsed
                })
                return RoleModel(**updated)
            else:
                L.warning({
                    "event": "REPO.ROLE.UPDATE.NOT_MODIFIED",
                    "role_id": role_id,
                    "time": elapsed
                })
                return None
        except PyMongoError as e:
            L.error({
                "event": "REPO.ROLE.UPDATE.FAIL",
                "role_id": role_id,
                "error": str(e)
            })
            return None

    async def delete(self, role_id: str) -> bool:
        t1 = T.time()
        try:
            result = await self.collection.delete_one({"role_id": role_id})
            elapsed = round(T.time() - t1, 4)
            success = result.deleted_count > 0
            L.debug({
                "event": "REPO.ROLE.DELETED",
                "role_id": role_id,
                "success": success,
                "time": elapsed
            })
            return success
        except PyMongoError as e:
            L.error({
                "event": "REPO.ROLE.DELETE.FAIL",
                "role_id": role_id,
                "error": str(e)
            })
            return False

