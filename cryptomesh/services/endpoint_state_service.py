import time as T
from fastapi import HTTPException
from typing import List
from cryptomesh.models import EndpointStateModel
from cryptomesh.repositories.endpoint_state_repository import EndpointStateRepository
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class EndpointStateService:
    """
    Servicio para gestionar los estados de los endpoints.
    """

    def __init__(self, repository: EndpointStateRepository):
        self.repository = repository

    async def create_state(self, state: EndpointStateModel) -> EndpointStateModel:
        t1 = T.time()
        if await self.repository.get_by_id(state.state_id):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "ENDPOINT_STATE.CREATE.FAIL",
                "reason": "Already exists",
                "state_id": state.state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=400, detail="Endpoint state already exists")

        created = await self.repository.create(state)
        elapsed = round(T.time() - t1, 4)

        if not created:
            L.error({
                "event": "ENDPOINT_STATE.CREATE.FAIL",
                "reason": "Failed to create",
                "state_id": state.state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to create endpoint state")

        L.info({
            "event": "ENDPOINT_STATE.CREATED",
            "state_id": state.state_id,
            "time": elapsed
        })
        return created

    async def list_states(self) -> List[EndpointStateModel]:
        t1 = T.time()
        states = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)

        L.debug({
            "event": "ENDPOINT_STATE.LISTED",
            "count": len(states),
            "time": elapsed
        })
        return states

    async def get_state(self, state_id: str) -> EndpointStateModel:
        t1 = T.time()
        state = await self.repository.get_by_id(state_id)
        elapsed = round(T.time() - t1, 4)

        if not state:
            L.warning({
                "event": "ENDPOINT_STATE.GET.NOT_FOUND",
                "state_id": state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Endpoint state not found")

        L.info({
            "event": "ENDPOINT_STATE.FETCHED",
            "state_id": state_id,
            "time": elapsed
        })
        return state

    async def update_state(self, state_id: str, updates: dict) -> EndpointStateModel:
        t1 = T.time()
        if not await self.repository.get_by_id(state_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ENDPOINT_STATE.UPDATE.NOT_FOUND",
                "state_id": state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Endpoint state not found")

        updated = await self.repository.update(state_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "ENDPOINT_STATE.UPDATE.FAIL",
                "state_id": state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to update endpoint state")

        L.info({
            "event": "ENDPOINT_STATE.UPDATED",
            "state_id": state_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_state(self, state_id: str) -> dict:
        t1 = T.time()
        if not await self.repository.get_by_id(state_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ENDPOINT_STATE.DELETE.NOT_FOUND",
                "state_id": state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Endpoint state not found")

        success = await self.repository.delete(state_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "ENDPOINT_STATE.DELETE.FAIL",
                "state_id": state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to delete endpoint state")

        L.info({
            "event": "ENDPOINT_STATE.DELETED",
            "state_id": state_id,
            "time": elapsed
        })
        return {"detail": f"Endpoint state '{state_id}' deleted"}
