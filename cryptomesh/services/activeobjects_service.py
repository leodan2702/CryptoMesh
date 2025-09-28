import time as T
from typing import List,Dict
import ast
from cryptomesh.models import ActiveObjectModel
from cryptomesh.repositories.activeobjects_repository import ActiveObjectsRepository
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError,
    CreationError,
)
from cryptomesh.dtos import SchemaDTO
from cryptomesh.utils import Utils


L = get_logger(__name__)

class ActiveObjectsService:
    """
    Servicio encargado de gestionar los Active Objects en la base de datos.
    """

    def __init__(self, repository: ActiveObjectsRepository):
        self.repository = repository

    async def create_active_object(self, active_object: ActiveObjectModel) -> ActiveObjectModel:
        t1 = T.time()
        if await self.repository.get_by_id(active_object.active_object_id, id_field="active_object_id"):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "ACTIVE_OBJECT.CREATE.FAIL",
                "reason": "Already exists",
                "active_object_id": active_object.active_object_id,
                "time": elapsed
            })
            raise ValidationError(f"ActiveObject '{active_object.active_object_id}' already exists")

        created = await self.repository.create(active_object)
        elapsed = round(T.time() - t1, 4)

        if not created:
            L.error({
                "event": "ACTIVE_OBJECT.CREATE.FAIL",
                "reason": "Failed to create",
                "active_object_id": active_object.active_object_id,
                "time": elapsed
            })
            raise CreationError(f"Failed to create ActiveObject '{active_object.active_object_id}'")

        L.info({
            "event": "ACTIVE_OBJECT.CREATED",
            "active_object_id": active_object.active_object_id,
            "time": elapsed
        })
        return created

    async def list_active_objects(self) -> List[ActiveObjectModel]:
        t1 = T.time()
        active_objects = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)
        L.debug({
            "event": "ACTIVE_OBJECT.LISTED",
            "count": len(active_objects),
            "time": elapsed
        })
        return active_objects

    async def get_active_object(self, active_object_id: str) -> ActiveObjectModel:
        t1 = T.time()
        ao = await self.repository.get_by_id(active_object_id, id_field="active_object_id")
        elapsed = round(T.time() - t1, 4)

        if not ao:
            L.warning({
                "event": "ACTIVE_OBJECT.GET.NOT_FOUND",
                "active_object_id": active_object_id,
                "time": elapsed
            })
            raise NotFoundError(active_object_id)

        L.info({
            "event": "ACTIVE_OBJECT.FETCHED",
            "active_object_id": active_object_id,
            "time": elapsed
        })
        return ao

    async def update_active_object(self, active_object_id: str, updates: dict) -> ActiveObjectModel:
        t1 = T.time()
        if not await self.repository.get_by_id(active_object_id, id_field="active_object_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ACTIVE_OBJECT.UPDATE.NOT_FOUND",
                "active_object_id": active_object_id,
                "time": elapsed
            })
            raise NotFoundError(active_object_id)

        updated = await self.repository.update({"active_object_id": active_object_id}, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "ACTIVE_OBJECT.UPDATE.FAIL",
                "active_object_id": active_object_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update ActiveObject '{active_object_id}'")

        L.info({
            "event": "ACTIVE_OBJECT.UPDATED",
            "active_object_id": active_object_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_active_object(self, active_object_id: str) -> dict:
        t1 = T.time()
        if not await self.repository.get_by_id(active_object_id, id_field="active_object_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ACTIVE_OBJECT.DELETE.NOT_FOUND",
                "active_object_id": active_object_id,
                "time": elapsed
            })
            raise NotFoundError(active_object_id)

        success = await self.repository.delete({"active_object_id": active_object_id})
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "ACTIVE_OBJECT.DELETE.FAIL",
                "active_object_id": active_object_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to delete ActiveObject '{active_object_id}'")

        L.info({
            "event": "ACTIVE_OBJECT.DELETED",
            "active_object_id": active_object_id,
            "time": elapsed
        })
        return {"detail": f"ActiveObject '{active_object_id}' deleted"}


