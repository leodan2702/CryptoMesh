import time as T
from cryptomesh.models import FunctionStateModel
from cryptomesh.repositories.function_state_repository import FunctionStateRepository
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

class FunctionStateService:
    """
    Servicio encargado de gestionar los estados de funciones en la base de datos.
    """

    def __init__(self, repository: FunctionStateRepository):
        self.repository = repository

    async def create_state(self, state: FunctionStateModel):
        t1 = T.time()
        if await self.repository.get_by_id(state.state_id):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "FUNCTION_STATE.CREATE.FAIL",
                "reason": "Already exists",
                "state_id": state.state_id,
                "time": elapsed
            })
            raise ValidationError(f"Function state '{state.state_id}' already exists")

        created = await self.repository.create(state)
        elapsed = round(T.time() - t1, 4)

        if not created:
            L.error({
                "event": "FUNCTION_STATE.CREATE.FAIL",
                "reason": "Failed to create",
                "state_id": state.state_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create function state '{state.state_id}'")

        L.info({
            "event": "FUNCTION_STATE.CREATED",
            "state_id": state.state_id,
            "time": elapsed
        })
        return created

    async def list_states(self):
        t1 = T.time()
        states = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)

        L.debug({
            "event": "FUNCTION_STATE.LISTED",
            "count": len(states),
            "time": elapsed
        })
        return states

    async def get_state(self, state_id: str):
        t1 = T.time()
        state = await self.repository.get_by_id(state_id)
        elapsed = round(T.time() - t1, 4)

        if not state:
            L.warning({
                "event": "FUNCTION_STATE.GET.NOT_FOUND",
                "state_id": state_id,
                "time": elapsed
            })
            raise NotFoundError(state_id)

        L.info({
            "event": "FUNCTION_STATE.FETCHED",
            "state_id": state_id,
            "time": elapsed
        })
        return state

    async def update_state(self, state_id: str, updates: dict):
        t1 = T.time()
        if not await self.repository.get_by_id(state_id, id_field="state_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "FUNCTION_STATE.UPDATE.NOT_FOUND",
                "state_id": state_id,
                "time": elapsed
            })
            raise NotFoundError(state_id)

        updated = await self.repository.update({"state_id": state_id}, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "FUNCTION_STATE.UPDATE.FAIL",
                "state_id": state_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update function state '{state_id}'")

        L.info({
            "event": "FUNCTION_STATE.UPDATED",
            "state_id": state_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_state(self, state_id: str):
        t1 = T.time()
        if not await self.repository.get_by_id(state_id, id_field="state_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "FUNCTION_STATE.DELETE.NOT_FOUND",
                "state_id": state_id,
                "time": elapsed
            })
            raise NotFoundError(state_id)

        success = await self.repository.delete({"state_id": state_id})
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "FUNCTION_STATE.DELETE.FAIL",
                "state_id": state_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to delete function state '{state_id}'")

        L.info({
            "event": "FUNCTION_STATE.DELETED",
            "state_id": state_id,
            "time": elapsed
        })
        return {"detail": f"Function state '{state_id}' deleted"}
