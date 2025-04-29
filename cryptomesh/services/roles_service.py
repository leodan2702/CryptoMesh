import time as T
from fastapi import HTTPException
from typing import List
from cryptomesh.models import RoleModel
from cryptomesh.repositories.roles_repository import RolesRepository
from cryptomesh.log import Log

# Logger configurado
L = Log(name=__name__)

class RolesService:
    """
    Servicio encargado de gestionar los roles en la base de datos.
    """

    def __init__(self, repository: RolesRepository):
        self.repository = repository

    async def create_role(self, role: RoleModel) -> RoleModel:
        t1 = T.time()
        if await self.repository.get_by_id(role.role_id):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "ROLE.CREATE.FAIL",
                "reason": "Already exists",
                "role_id": role.role_id,
                "time": elapsed
            })
            raise HTTPException(status_code=400, detail="Role already exists")

        created = await self.repository.create(role)
        elapsed = round(T.time() - t1, 4)

        if not created:
            L.error({
                "event": "ROLE.CREATE.FAIL",
                "reason": "Failed to create",
                "role_id": role.role_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to create role")

        L.info({
            "event": "ROLE.CREATED",
            "role_id": role.role_id,
            "time": elapsed
        })
        return created

    async def list_roles(self) -> List[RoleModel]:
        t1 = T.time()
        roles = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)
        L.debug({
            "event": "ROLE.LISTED",
            "count": len(roles),
            "time": elapsed
        })
        return roles

    async def get_role(self, role_id: str) -> RoleModel:
        t1 = T.time()
        role = await self.repository.get_by_id(role_id)
        elapsed = round(T.time() - t1, 4)

        if not role:
            L.warning({
                "event": "ROLE.GET.NOT_FOUND",
                "role_id": role_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Role not found")

        L.info({
            "event": "ROLE.FETCHED",
            "role_id": role_id,
            "time": elapsed
        })
        return role

    async def update_role(self, role_id: str, updates: dict) -> RoleModel:
        t1 = T.time()
        if not await self.repository.get_by_id(role_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ROLE.UPDATE.NOT_FOUND",
                "role_id": role_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Role not found")

        updated = await self.repository.update(role_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "ROLE.UPDATE.FAIL",
                "role_id": role_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to update role")

        L.info({
            "event": "ROLE.UPDATED",
            "role_id": role_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_role(self, role_id: str) -> dict:
        t1 = T.time()
        if not await self.repository.get_by_id(role_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ROLE.DELETE.NOT_FOUND",
                "role_id": role_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Role not found")

        success = await self.repository.delete(role_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "ROLE.DELETE.FAIL",
                "role_id": role_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to delete role")

        L.info({
            "event": "ROLE.DELETED",
            "role_id": role_id,
            "time": elapsed
        })
        return {"detail": f"Role '{role_id}' deleted"}
