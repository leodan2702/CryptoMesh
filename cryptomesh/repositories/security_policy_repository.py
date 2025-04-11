from motor.motor_asyncio import AsyncIOMotorCollection
from pymongo.errors import PyMongoError
from pymongo import ReturnDocument
from typing import Optional, List
from cryptomesh.models import SecurityPolicyModel

class SecurityPolicyRepository:
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection

    async def create(self, policy: SecurityPolicyModel) -> Optional[SecurityPolicyModel]:
        try:
            policy_dict = policy.dict(by_alias=True, exclude_unset=True)
            result = await self.collection.insert_one(policy_dict)
            if result.inserted_id:
                return policy
            return None
        except PyMongoError as e:
            print(f"❌ Error creating security policy: {e}")
            return None
    
    async def get_all(self) -> List[SecurityPolicyModel]:
        policies = []
        cursor = self.collection.find({})
        async for document in cursor:
            policies.append(SecurityPolicyModel(**document))
        return policies

    async def get_by_id(self, sp_id: str) -> Optional[SecurityPolicyModel]:
        document = await self.collection.find_one({"sp_id": sp_id})
        if document:
            return SecurityPolicyModel(**document)
        return None

    async def update(self, sp_id: str, updates: dict) -> Optional[SecurityPolicyModel]:
        try:
            updated = await self.collection.find_one_and_update(
                {"sp_id": sp_id},
                {"$set": updates},
                return_document=ReturnDocument.AFTER
            )
            if updated:
                return SecurityPolicyModel(**updated)
            return None
        except PyMongoError as e:
            print(f"❌ Error updating security policy: {e}")
            return None

    async def delete(self, sp_id: str) -> bool:
        try:
            result = await self.collection.delete_one({"sp_id": sp_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            print(f"❌ Error deleting security policy: {e}")
            return False

