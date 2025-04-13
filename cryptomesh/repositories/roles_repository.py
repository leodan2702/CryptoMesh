from motor.motor_asyncio import AsyncIOMotorCollection
from typing import List, Optional
from pymongo.errors import PyMongoError
from cryptomesh.models import RoleModel

class RolesRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, role: RoleModel) -> Optional[RoleModel]:
        try:
            role_dict = role.model_dump(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(role_dict)
            if result.inserted_id:
                return role
            return None
        except PyMongoError as e:
            print(f"❌ Error al crear role: {e}")
            return None

    async def get_all(self) -> List[RoleModel]:
        roles = []
        cursor = self.collection.find({})
        async for document in cursor:
            roles.append(RoleModel(**document))
        return roles

    async def get_by_id(self, role_id: str) -> Optional[RoleModel]:
        document = await self.collection.find_one({"role_id": role_id})
        if document:
            return RoleModel(**document)
        return None

    async def update(self, role_id: str, updates: dict) -> Optional[RoleModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"role_id": role_id},
                {"$set": updates},
                return_document=True  # Para versiones modernas de pymongo puedes usar ReturnDocument.AFTER
            )
            if updated:
                return RoleModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error al actualizar role: {e}")
            return None

    async def delete(self, role_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"role_id": role_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error al eliminar role: {e}")
            return False
