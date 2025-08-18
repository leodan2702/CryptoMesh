import time as T
from cryptomesh.models import EndpointModel
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
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

class EndpointsService:
    """
    Servicio encargado de gestionar los endpoints y sus relaciones con las políticas de seguridad.
    """

    def __init__(self, repository: EndpointsRepository, security_policy_service: SecurityPolicyService):
        self.repository = repository
        self.security_policy_service = security_policy_service

    async def create_endpoint(self, data: EndpointModel):
        t1 = T.time()
        # pasar id_field para que get_by_id busque por "endpoint_id"
        if await self.repository.get_by_id(data.endpoint_id, id_field="endpoint_id"):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "ENDPOINT.CREATE.FAIL",
                "reason": "Already exists",
                "endpoint_id": data.endpoint_id,
                "time": elapsed
            })
            raise ValidationError(f"Endpoint '{data.endpoint_id}' already exists")

        endpoint = await self.repository.create(data)
        elapsed = round(T.time() - t1, 4)

        if not endpoint:
            L.error({
                "event": "ENDPOINT.CREATE.FAIL",
                "reason": "Failed to create",
                "endpoint_id": data.endpoint_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create endpoint '{data.endpoint_id}'")

        L.info({
            "event": "ENDPOINT.CREATED",
            "endpoint_id": endpoint.endpoint_id,
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
        endpoint = await self.repository.get_by_id(endpoint_id, id_field="endpoint_id")
        elapsed = round(T.time() - t1, 4)

        if not endpoint:
            L.warning({
                "event": "ENDPOINT.GET.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise NotFoundError(endpoint_id)

        L.info({
            "event": "ENDPOINT.FETCHED",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        
        return endpoint

        # --- Manejo de SecurityPolicy incrustada ---
        sp_id = None
        if hasattr(endpoint.security_policy, 'sp_id'):
            sp_id = endpoint.security_policy.sp_id
        else:
            sp_id = endpoint.security_policy

        sp = None
        if sp_id:
            sp = await self.security_policy_service.get_policy(sp_id)

        endpoint_data = endpoint.model_dump()
        if sp:
            endpoint_data['security_policy'] = sp.model_dump()
        else:
            endpoint_data['security_policy'] = endpoint.security_policy


        

    async def update_endpoint(self, endpoint_id: str, updates: dict): 
        t1 = T.time()
        if not await self.repository.get_by_id(endpoint_id, id_field="endpoint_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ENDPOINT.UPDATE.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise NotFoundError(endpoint_id)

        updated = await self.repository.update({"endpoint_id": endpoint_id}, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "ENDPOINT.UPDATE.FAIL",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update endpoint '{endpoint_id}'")

        L.info({
            "event": "ENDPOINT.UPDATED",
            "endpoint_id": endpoint_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_endpoint(self, endpoint_id: str):
        t1 = T.time()
        # pasar id_field para buscar por "endpoint_id"
        if not await self.repository.get_by_id(endpoint_id, id_field="endpoint_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ENDPOINT.DELETE.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise NotFoundError(endpoint_id)

        # Cambio: query debe ser dict de acuerdo a base_repository.py
        success = await self.repository.delete({"endpoint_id": endpoint_id})
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "ENDPOINT.DELETE.FAIL",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to delete endpoint '{endpoint_id}'")

        L.info({
            "event": "ENDPOINT.DELETED",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        return {"detail": f"Endpoint '{endpoint_id}' deleted"}

