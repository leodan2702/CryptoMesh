from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.repositories.base_repository import BaseRepository
from typing import Optional

class SecurityPolicyRepository(BaseRepository[SecurityPolicyModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, SecurityPolicyModel)

    async def get_by_id(self, sp_id: str, id_field: str = "sp_id") -> Optional[SecurityPolicyModel]:
        # Llama al método base directamente sin super()
        document = await self.collection.find_one({"sp_id": sp_id})
        return SecurityPolicyModel(**document) if document else None
