import time as T
from typing import List
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
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

class SecurityPolicyService:
    """
    Servicio encargado de manejar políticas de seguridad en la base de datos.
    """

    def __init__(self, repository: SecurityPolicyRepository):
        self.repository = repository

    async def create_policy(self, policy: SecurityPolicyModel) -> SecurityPolicyModel:
        t1 = T.time()
        if await self.repository.get_by_id(policy.sp_id):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "POLICY.CREATE.FAIL",
                "reason": "Already exists",
                "sp_id": policy.sp_id,
                "time": elapsed
            })
            raise ValidationError(f"Security policy '{policy.sp_id}' already exists")

        new_policy = await self.repository.create(policy)
        elapsed = round(T.time() - t1, 4)

        if not new_policy:
            L.error({
                "event": "POLICY.CREATE.FAIL",
                "reason": "Failed to create",
                "sp_id": policy.sp_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create security policy '{policy.sp_id}'")

        L.info({
            "event": "POLICY.CREATED",
            "sp_id": policy.sp_id,
            "time": elapsed
        })
        return new_policy

    async def list_policies(self) -> List[SecurityPolicyModel]:
        t1 = T.time()
        policies = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)
        L.debug({
            "event": "POLICY.LISTED",
            "count": len(policies),
            "time": elapsed
        })
        return policies

    async def get_policy(self, sp_id: str) -> SecurityPolicyModel:
        t1 = T.time()
        policy = await self.repository.get_by_id(sp_id)
        elapsed = round(T.time() - t1, 4)

        if not policy:
            L.warning({
                "event": "POLICY.GET.NOT_FOUND",
                "sp_id": sp_id,
                "time": elapsed
            })
            raise NotFoundError(sp_id)

        L.info({
            "event": "POLICY.FETCHED",
            "sp_id": sp_id,
            "time": elapsed
        })
        return policy

    async def update_policy(self, sp_id: str, updates: dict) -> SecurityPolicyModel:
        t1 = T.time()
        if not await self.repository.get_by_id(sp_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "POLICY.UPDATE.NOT_FOUND",
                "sp_id": sp_id,
                "time": elapsed
            })
            raise NotFoundError(sp_id)

        updated_policy = await self.repository.update(sp_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated_policy:
            L.error({
                "event": "POLICY.UPDATE.FAIL",
                "sp_id": sp_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update security policy '{sp_id}'")

        L.info({
            "event": "POLICY.UPDATED",
            "sp_id": sp_id,
            "updates": updates,
            "time": elapsed
        })
        return updated_policy

    async def delete_policy(self, sp_id: str) -> dict:
        t1 = T.time()
        if not await self.repository.get_by_id(sp_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "POLICY.DELETE.NOT_FOUND",
                "sp_id": sp_id,
                "time": elapsed
            })
            raise NotFoundError(sp_id)

        success = await self.repository.delete(sp_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "POLICY.DELETE.FAIL",
                "sp_id": sp_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to delete security policy '{sp_id}'")

        L.info({
            "event": "POLICY.DELETED",
            "sp_id": sp_id,
            "time": elapsed
        })
        return {"detail": f"Security policy '{sp_id}' deleted"}


