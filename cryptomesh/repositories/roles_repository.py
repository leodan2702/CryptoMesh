from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import RoleModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class RolesRepository(BaseRepository[RoleModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, RoleModel)

    async def get_by_id(self, role_id: str, id_field: str = "role_id") -> Optional[RoleModel]:
        document = await self.collection.find_one({"role_id": role_id})
        return RoleModel(**document) if document else None
