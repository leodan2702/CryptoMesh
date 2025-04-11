from fastapi import HTTPException
from typing import List
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository

class SecurityPolicyService:
    def __init__(self, repository: SecurityPolicyRepository):
        self.repository = repository

    async def create_policy(self, policy: SecurityPolicyModel):
        existing = await self.repository.get_by_id(policy.sp_id)
        if existing:
            raise HTTPException(status_code=400, detail="Security policy already exists")
        new_policy = await self.repository.create(policy)
        if not new_policy:
            raise HTTPException(status_code=500, detail="Failed to create security policy")
        return new_policy

    async def list_policies(self) -> List[SecurityPolicyModel]:
        return await self.repository.get_all()

    async def get_policy(self, sp_id: str):
        policy = await self.repository.get_by_id(sp_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Security policy not found")
        return policy

    async def update_policy(self, sp_id: str, updates: dict):
        policy = await self.repository.get_by_id(sp_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Security policy not found")
        updated_policy = await self.repository.update(sp_id, updates)
        if not updated_policy:
            raise HTTPException(status_code=500, detail="Failed to update security policy")
        return updated_policy

    async def delete_policy(self, sp_id: str):
        policy = await self.repository.get_by_id(sp_id)
        if not policy:
            raise HTTPException(status_code=404, detail="Security policy not found")
        success = await self.repository.delete(sp_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete security policy")
        return {"detail": f"Security policy '{sp_id}' deleted"}

