from fastapi import HTTPException
from typing import List
from cryptomesh.models import RoleModel
from cryptomesh.repositories.roles_repository import RolesRepository

class RolesService:
    def __init__(self, repository: RolesRepository):
        self.repository = repository

    async def create_role(self, role: RoleModel) -> RoleModel:
        if await self.repository.get_by_id(role.role_id):
            raise HTTPException(status_code=400, detail="Role already exists")
        created = await self.repository.create(role)
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create role")
        return created

    async def list_roles(self) -> List[RoleModel]:
        return await self.repository.get_all()

    async def get_role(self, role_id: str) -> RoleModel:
        role = await self.repository.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        return role

    async def update_role(self, role_id: str, updates: dict) -> RoleModel:
        if not await self.repository.get_by_id(role_id):
            raise HTTPException(status_code=404, detail="Role not found")
        updated = await self.repository.update(role_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update role")
        return updated

    async def delete_role(self, role_id: str) -> dict:
        if not await self.repository.get_by_id(role_id):
            raise HTTPException(status_code=404, detail="Role not found")
        success = await self.repository.delete(role_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete role")
        return {"detail": f"Role '{role_id}' deleted"}
