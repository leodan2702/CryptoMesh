# cryptomesh/services/endpoints_services.py
from fastapi import HTTPException
from cryptomesh.models import EndpointModel, SecurityPolicyModel
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService  # Asegúrate de contar con este servicio

class EndpointsService:
    def __init__(self, repository: EndpointsRepository, security_policy_service: SecurityPolicyService):
        self.repository = repository
        self.security_policy_service = security_policy_service

    async def create_endpoint(self, data: EndpointModel):
        if await self.repository.get_by_id(data.endpoint_id):
            raise HTTPException(status_code=400, detail="Endpoint already exists")
        endpoint = await self.repository.create(data)
        if not endpoint:
            raise HTTPException(status_code=500, detail="Failed to create endpoint")
        return endpoint

    async def list_endpoints(self):
        endpoints = await self.repository.get_all()
        # Puedes, opcionalmente, resolver la política de seguridad para cada endpoint aquí
        return endpoints

    async def get_endpoint(self, endpoint_id: str):
        endpoint = await self.repository.get_by_id(endpoint_id)
        if not endpoint:
            raise HTTPException(status_code=404, detail="Endpoint not found")
        # En lugar de enviar el ID de security_policy, obtenemos los roles mediante el SecurityPolicyService
        sp = await self.security_policy_service.get_by_id(endpoint.security_policy)
        endpoint_data = endpoint.dict()
        # Si se encontró la política, reemplazamos el valor por los roles; si no, dejamos el ID
        endpoint_data['security_policy'] = sp.roles if sp else endpoint.security_policy
        return EndpointModel(**endpoint_data)

    async def update_endpoint(self, endpoint_id: str, updates: dict):
        if not await self.repository.get_by_id(endpoint_id):
            raise HTTPException(status_code=404, detail="Endpoint not found")
        updated = await self.repository.update(endpoint_id, updates)
        if not updated:
            raise HTTPException(status_code=500, detail="Failed to update endpoint")
        return updated

    async def delete_endpoint(self, endpoint_id: str):
        if not await self.repository.get_by_id(endpoint_id):
            raise HTTPException(status_code=404, detail="Endpoint not found")
        success = await self.repository.delete(endpoint_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete endpoint")
        return {"detail": f"Endpoint '{endpoint_id}' deleted"}


