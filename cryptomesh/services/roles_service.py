import time as T
from typing import List
from cryptomesh.models import RoleModel
from cryptomesh.repositories.roles_repository import RolesRepository
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError,
    InvalidYAML,
    CreationError,
    UnauthorizedError,
    FunctionNotFound,
)

L = get_logger(__name__)

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
            raise ValidationError(f"Role '{role.role_id}' already exists")

        created = await self.repository.create(role)
        elapsed = round(T.time() - t1, 4)

        if not created:
            L.error({
                "event": "ROLE.CREATE.FAIL",
                "reason": "Failed to create",
                "role_id": role.role_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create role '{role.role_id}'")

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
            raise NotFoundError(role_id)

        L.info({
            "event": "ROLE.FETCHED",
            "role_id": role_id,
            "time": elapsed
        })
        return role

    async def update_role(self, role_id: str, updates: dict) -> RoleModel:
        t1 = T.time()
        if not await self.repository.get_by_id(role_id, id_field="role_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ROLE.UPDATE.NOT_FOUND",
                "role_id": role_id,
                "time": elapsed
            })
            raise NotFoundError(role_id)

        updated = await self.repository.update({"role_id": role_id}, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "ROLE.UPDATE.FAIL",
                "role_id": role_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update role '{role_id}'")

        L.info({
            "event": "ROLE.UPDATED",
            "role_id": role_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_role(self, role_id: str) -> dict:
        t1 = T.time()
        if not await self.repository.get_by_id(role_id, id_field="role_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ROLE.DELETE.NOT_FOUND",
                "role_id": role_id,
                "time": elapsed
            })
            raise NotFoundError(role_id)

        success = await self.repository.delete({"role_id": role_id})
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "ROLE.DELETE.FAIL",
                "role_id": role_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to delete role '{role_id}'")

        L.info({
            "event": "ROLE.DELETED",
            "role_id": role_id,
            "time": elapsed
        })
        return {"detail": f"Role '{role_id}' deleted"}
