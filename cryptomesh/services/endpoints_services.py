# cryptomesh/services/endpoints_services.py
import time as T
from fastapi import HTTPException
from cryptomesh.models import EndpointModel
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.log import Log

# Logger configurado
L = Log(name=__name__)

class EndpointsService:
    """
    Servicio encargado de gestionar los endpoints y sus relaciones con las políticas de seguridad.
    """

    def __init__(self, repository: EndpointsRepository, security_policy_service: SecurityPolicyService):
        self.repository = repository
        self.security_policy_service = security_policy_service

    async def create_endpoint(self, data: EndpointModel):
        t1 = T.time()
        if await self.repository.get_by_id(data.endpoint_id):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "ENDPOINT.CREATE.FAIL",
                "reason": "Already exists",
                "endpoint_id": data.endpoint_id,
                "time": elapsed
            })
            raise HTTPException(status_code=400, detail="Endpoint already exists")

        endpoint = await self.repository.create(data)
        elapsed = round(T.time() - t1, 4)

        if not endpoint:
            L.error({
                "event": "ENDPOINT.CREATE.FAIL",
                "reason": "Failed to create",
                "endpoint_id": data.endpoint_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to create endpoint")

        L.info({
            "event": "ENDPOINT.CREATED",
            "endpoint_id": data.endpoint_id,
            "time": elapsed
        })
        return endpoint

    async def list_endpoints(self):
        t1 = T.time()
        endpoints = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)

        L.debug({
            "event": "ENDPOINT.LISTED",
            "count": len(endpoints),
            "time": elapsed
        })
        return endpoints

    async def get_endpoint(self, endpoint_id: str):
        t1 = T.time()
        endpoint = await self.repository.get_by_id(endpoint_id)
        elapsed = round(T.time() - t1, 4)

        if not endpoint:
            L.warning({
                "event": "ENDPOINT.GET.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Endpoint not found")

        # Buscamos la política de seguridad asociada
        sp = await self.security_policy_service.get_policy(endpoint.security_policy)

        endpoint_data = endpoint.model_dump()
        endpoint_data['security_policy'] = sp.sp_id if sp else endpoint.security_policy

        L.info({
            "event": "ENDPOINT.FETCHED",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        return EndpointModel(**endpoint_data)

    async def update_endpoint(self, endpoint_id: str, updates: dict) -> EndpointModel:
        t1 = T.time()
        if not await self.repository.get_by_id(endpoint_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ENDPOINT.UPDATE.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Endpoint not found")

        updated = await self.repository.update(endpoint_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "ENDPOINT.UPDATE.FAIL",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to update endpoint")

        L.info({
            "event": "ENDPOINT.UPDATED",
            "endpoint_id": endpoint_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_endpoint(self, endpoint_id: str):
        t1 = T.time()
        if not await self.repository.get_by_id(endpoint_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ENDPOINT.DELETE.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Endpoint not found")

        success = await self.repository.delete(endpoint_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "ENDPOINT.DELETE.FAIL",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to delete endpoint")

        L.info({
            "event": "ENDPOINT.DELETED",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        return {"detail": f"Endpoint '{endpoint_id}' deleted"}
