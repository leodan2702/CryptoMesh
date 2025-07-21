import httpx
import json
import time
from typing import Optional, Dict, Any, List
from cryptomesh.log.logger import get_logger
from cryptomesh.models import * 
from option import Ok,Err,Result

L = get_logger("cryptomesh-client")

class CryptoMeshClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    # -------------------- Function --------------------

    async def create_function(self, function: FunctionModel) -> Result[FunctionModel,Exception]:
        payload = json.loads(function.model_dump_json(by_alias=True))
        data = await self._post("/api/v1/functions/", payload)
        return data
        # return FunctionModel(**data)

    async def get_function(self, function_id: str) -> FunctionModel:
        data = await self._get(f"/api/v1/functions/{function_id}/")
        return FunctionModel(**data)

    async def list_functions(self) -> List[FunctionModel]:
        data = await self._get("/api/v1/functions/")
        return [FunctionModel(**item) for item in data]

    async def delete_function(self, function_id: str) -> bool:
        await self._delete(f"/api/v1/functions/{function_id}/")
        return True

    # -------------------- Service --------------------

    async def create_service(self, service: ServiceModel) -> ServiceModel:
        payload = json.loads(service.model_dump_json(by_alias=True))
        data = await self._post("/api/v1/services/", payload)
        return ServiceModel(**data)

    async def get_service(self, service_id: str) -> ServiceModel:
        data = await self._get(f"/api/v1/services/{service_id}/")
        return ServiceModel(**data)

    async def list_services(self) -> List[ServiceModel]:
        data = await self._get("/api/v1/services/")
        return [ServiceModel(**item) for item in data]

    async def delete_service(self, service_id: str) -> bool:
        await self._delete(f"/api/v1/services/{service_id}/")
        return True

    # -------------------- Microservice --------------------

    async def create_microservice(self, microservice: MicroserviceModel) -> MicroserviceModel:
        payload = json.loads(microservice.model_dump_json(by_alias=True))
        data = await self._post("/api/v1/microservices/", payload)
        return MicroserviceModel(**data)

    async def get_microservice(self, microservice_id: str) -> MicroserviceModel:
        data = await self._get(f"/api/v1/microservices/{microservice_id}/")
        return MicroserviceModel(**data)

    async def list_microservices(self) -> List[MicroserviceModel]:
        data = await self._get("/api/v1/microservices/")
        return [MicroserviceModel(**item) for item in data]

    async def delete_microservice(self, microservice_id: str) -> bool:
        await self._delete(f"/api/v1/microservices/{microservice_id}/")
        return True

    # -------------------- Endpoint --------------------

    async def create_endpoint(self, endpoint: EndpointModel) -> EndpointModel:
        payload = json.loads(endpoint.model_dump_json(by_alias=True))
        data = await self._post("/api/v1/endpoints/", payload)
        return EndpointModel(**data)

    async def get_endpoint(self, endpoint_id: str) -> EndpointModel:
        data = await self._get(f"/api/v1/endpoints/{endpoint_id}/")
        return EndpointModel(**data)

    async def list_endpoints(self) -> List[EndpointModel]:
        data = await self._get("/api/v1/endpoints/")
        return [EndpointModel(**item) for item in data]

    async def delete_endpoint(self, endpoint_id: str) -> bool:
        await self._delete(f"/api/v1/endpoints/{endpoint_id}/")
        return True

    # -------------------- SecurityPolicy --------------------

    async def create_security_policy(self, policy: SecurityPolicyModel) -> SecurityPolicyModel:
        payload = json.loads(policy.model_dump_json(by_alias=True))
        data = await self._post("/api/v1/security-policies/", payload)
        return SecurityPolicyModel(**data)

    async def get_security_policy(self, sp_id: str) -> SecurityPolicyModel:
        data = await self._get(f"/api/v1/security-policies/{sp_id}/")
        return SecurityPolicyModel(**data)

    async def list_security_policies(self) -> List[SecurityPolicyModel]:
        data = await self._get("/api/v1/security-policies/")
        return [SecurityPolicyModel(**item) for item in data]

    async def delete_security_policy(self, sp_id: str) -> bool:
        await self._delete(f"/api/v1/security-policies/{sp_id}/")
        return True

    # -------------------- Role --------------------

    async def create_role(self, role: RoleModel) -> RoleModel:
        payload = json.loads(role.model_dump_json(by_alias=True))
        data = await self._post("/api/v1/roles/", payload)
        return RoleModel(**data)

    async def get_role(self, role_id: str) -> RoleModel:
        data = await self._get(f"/api/v1/roles/{role_id}/")
        return RoleModel(**data)

    async def list_roles(self) -> List[RoleModel]:
        data = await self._get("/api/v1/roles/")
        return [RoleModel(**item) for item in data]

    async def delete_role(self, role_id: str) -> bool:
        await self._delete(f"/api/v1/roles/{role_id}/")
        return True

    # -------------------- FunctionState --------------------

    async def list_function_states(self) -> List[FunctionStateModel]:
        data = await self._get("/api/v1/function-states/")
        return [FunctionStateModel(**item) for item in data]

    # -------------------- FunctionResult --------------------

    async def list_function_results(self) -> List[FunctionResultModel]:
        data = await self._get("/api/v1/function-results/")
        return [FunctionResultModel(**item) for item in data]

    # -------------------- EndpointState --------------------

    async def list_endpoint_states(self) -> List[EndpointStateModel]:
        data = await self._get("/api/v1/endpoint-states/")
        return [EndpointStateModel(**item) for item in data]

    async def get_endpoint_state(self, state_id: str) -> EndpointStateModel:
        data = await self._get(f"/api/v1/endpoint-states/{state_id}/")
        return EndpointStateModel(**data)

    async def delete_endpoint_state(self, state_id: str) -> bool:
        await self._delete(f"/api/v1/endpoint-states/{state_id}/")
        return True

    # -------------------- Internal HTTP Methods --------------------

    async def _get(self, path: str, headers: Dict[str, str] = {}) -> Any:
        url = f"{self.base_url}{path}"
        full_headers = {**self.headers, **headers}
        t1 = time.time()
        async with httpx.AsyncClient(headers=full_headers, follow_redirects=True) as client:
            response = await client.get(url)
        L.info({"event": "GET", "path": path, "status": response.status_code, "elapsed": round(time.time() - t1, 3)})
        response.raise_for_status()
        return response.json()

    async def _post(self, path: str, payload: Dict[str, Any], headers: Dict[str, str] = {}) -> Result[Any,Exception]:
        try:
            url = f"{self.base_url}{path}"
            full_headers = {**self.headers, **headers}
            t1 = time.time()
            async with httpx.AsyncClient(headers=full_headers, follow_redirects=True) as client:
                response = await client.post(url, json=payload)
            L.info({"event": "POST", "path": path, "status": response.status_code, "elapsed": round(time.time() - t1, 3)})
            response.raise_for_status()
            return Ok(response.json() if response.content else {})
        except Exception as e:
            return Err(e)

    async def _put(self, path: str, payload: Any, headers: Dict[str, str] = {}) -> Any:
        url = f"{self.base_url}{path}"
        full_headers = {**self.headers, **headers}
        t1 = time.time()
        async with httpx.AsyncClient(headers=full_headers, follow_redirects=True) as client:
            response = await client.put(url, json=payload)
        L.info({"event": "PUT", "path": path, "status": response.status_code, "elapsed": round(time.time() - t1, 3)})
        response.raise_for_status()
        return response.json() if response.content else {}

    async def _delete(self, path: str, headers: Dict[str, str] = {}) -> Any:
        url = f"{self.base_url}{path}"
        full_headers = {**self.headers, **headers}
        t1 = time.time()
        async with httpx.AsyncClient(headers=full_headers, follow_redirects=True) as client:
            response = await client.delete(url)
        L.info({"event": "DELETE", "path": path, "status": response.status_code, "elapsed": round(time.time() - t1, 3)})
        response.raise_for_status()
        return True if response.status_code == 204 else response.json()