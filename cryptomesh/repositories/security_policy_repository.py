from motor.motor_asyncio import AsyncIOMotorCollection
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.repositories.base_repository import BaseRepository
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class SecurityPolicyRepository(BaseRepository[SecurityPolicyModel]):
    def __init__(self, collection: AsyncIOMotorCollection):
        super().__init__(collection, SecurityPolicyModel)



