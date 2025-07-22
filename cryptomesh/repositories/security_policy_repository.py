from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.repositories.base_repository import BaseRepository

class SecurityPolicyRepository(BaseRepository[SecurityPolicyModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, SecurityPolicyModel)

