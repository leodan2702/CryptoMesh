from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from cryptomesh.log.logger import get_logger
from cryptomesh.policies import CMPolicyManager
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError,
    InvalidYAML,
    CreationError,
    UnauthorizedError,
    FunctionNotFound,
)
import httpx
import json
import time
from cryptomesh.dtos import *
from typing import Optional, Dict, Any, List
from cryptomesh.log.logger import get_logger
from option import Ok,Err,Result

L = get_logger("cryptomesh-client")

class CryptoMeshClient:
    def __init__(self, base_url: str, token: Optional[str] = None):
        self.base_url = base_url.rstrip("/")
        self.headers = {"Content-Type": "application/json"}
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    async def interpret(self, policy_file: str):
        logger = get_logger(__name__)
        
        try:
            manager = CMPolicyManager(policy_file)
            models = manager.as_models()
        except Exception as e:
            logger.error({
                "event": "POLICY.LOAD.FAIL",
                "reason": str(e),
                "policy_file": policy_file
            }, exc_info=True)
            raise InvalidYAML(f"Failed to load policy file: {str(e)}")

        # Crear endpoints
        for eid, endpoint in models["endpoints"].items():
            try:
                await self.create_endpoint(endpoint)
                logger.info({"event": "ENDPOINT.CREATED", "id": eid})
            except Exception as e:
                logger.error(CreationError("endpoint", eid, e).to_dict())

        # Crear funciones
        for fid, function in models["functions"].items():
            try:
                await self.create_function(function)
                logger.info({"event": "FUNCTION.CREATED", "id": fid})
            except Exception as e:
                logger.error(CreationError("function", fid, e).to_dict())

        # Crear microservicios
        for msid, microservice in models["microservices"].items():
            try:
                await self.create_microservice(microservice)
                logger.info({"event": "MICROSERVICE.CREATED", "id": msid})
            except Exception as e:
                logger.error(CreationError("microservice", msid, e).to_dict())

        # Crear servicios
        for sid, service in models["services"].items():
            try:
                await self.create_service(service)
                logger.info({"event": "SERVICE.CREATED", "id": sid})
            except Exception as e:
                logger.error(CreationError("service", sid, e).to_dict())

    async def _handle_response(self, response: httpx.Response) -> Any:
        """Centralized response handler with custom error processing"""
        if response.is_success:
            return response.json() if response.content else {}
        
        try:
            error_data = response.json()
            message = error_data.get("message", response.text)
            code = error_data.get("code", "unknown_error")
        except json.JSONDecodeError:
            message = response.text
            code = "unknown_error"
        
        if response.status_code == 400:
            if code == "invalid_yaml":
                raise InvalidYAML(message)
            elif code == "validation_error":
                raise ValidationError(message)
            else:
                raise CryptoMeshError(message, code)
        elif response.status_code == 401:
            raise UnauthorizedError(message)
        elif response.status_code == 404:
            if code == "function_not_found":
                raise FunctionNotFound(message.split("'")[1])
            else:
                raise NotFoundError(message.split("'")[1] if "'" in message else message)
        elif response.status_code == 422:
            raise ValidationError(message)
        else:
            raise CryptoMeshError(message, code)

    # -------------------- Function Methods --------------------
    async def create_function(self, function: FunctionCreateDTO) -> Result[FunctionResponseDTO, CreationError]:
        try:
            # Serializar DTO
            payload = function.model_dump(by_alias=True)

            #Llamada al backend
            result = await self._post("/api/v1/functions/", payload)

             # Si _post retorna un Result
            if isinstance(result, Err):
                return result  # Pasar el error directamente
            response_data = result.unwrap() if isinstance(result, Ok) else result

            # Crear DTO de respuesta
            return Ok(FunctionResponseDTO(**response_data))

        except Exception as e:
            # No asumimos que function_id exista
            func_id = getattr(function, "function_id", "<unknown>")
            return Err(CreationError("function", func_id, e))


    async def get_function(self, function_id: str) -> FunctionResponseDTO:
        data = await self._get(f"/api/v1/functions/{function_id}/")
        return FunctionResponseDTO(**data)

    async def list_functions(self) -> List[FunctionResponseDTO]:
        data = await self._get("/api/v1/functions/")
        return [FunctionResponseDTO(**item) for item in data]

    async def delete_function(self, function_id: str) -> bool:
        await self._delete(f"/api/v1/functions/{function_id}/")
        return True

    # -------------------- Service Methods --------------------
    async def create_service(self, service: ServiceCreateDTO) -> Result[ServiceResponseDTO, CreationError]:
        try:
            payload = service.model_dump(by_alias=True)
            data = await self._post("/api/v1/services/", payload)
            return Ok(ServiceResponseDTO(**data))
        except Exception as e:
            return Err(CreationError("service", service.service_id, e))

    async def get_service(self, service_id:str) -> ServiceResponseDTO:
        data = await self._get(f"/api/v1/services/{service_id}/")
        return ServiceResponseDTO(**data)

    async def list_services(self) -> List[ServiceResponseDTO]:
        data = await self._get("/api/v1/services/")
        return [ServiceResponseDTO(**item) for item in data]

    async def delete_service(self, service_id: str) -> bool:
        await self._delete(f"/api/v1/services/{service_id}/")
        return True

    # -------------------- Microservice Methods --------------------
    async def create_microservice(self, microservice: MicroserviceCreateDTO) -> Result[MicroserviceResponseDTO, CreationError]:
        try:
            payload = microservice.model_dump(by_alias=True)
            data = await self._post("/api/v1/microservices/", payload)
            return Ok(MicroserviceResponseDTO(**data))
        except Exception as e:
            return Err(CreationError("microservice", microservice.microservice_id, e))

    async def get_microservice(self, microservice_id: str) -> MicroserviceResponseDTO:
        data = await self._get(f"/api/v1/microservices/{microservice_id}/")
        return MicroserviceResponseDTO(**data)

    async def list_microservices(self) -> List[MicroserviceResponseDTO]:
        data = await self._get("/api/v1/microservices/")
        return [MicroserviceResponseDTO(**item) for item in data]

    async def delete_microservice(self, microservice_id: str) -> bool:
        await self._delete(f"/api/v1/microservices/{microservice_id}/")
        return True

    # -------------------- Endpoint Methods --------------------
    async def create_endpoint(self, endpoint: EndpointCreateDTO) -> Result[EndpointResponseDTO,Exception]:
        payload = endpoint.model_dump(by_alias=True)
        data = await self._post("/api/v1/endpoints/", payload)
        if data.is_ok:
            return Ok(EndpointResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
    
    


    async def get_endpoint(self, endpoint_id: str) -> EndpointResponseDTO:
        data = await self._get(f"/api/v1/endpoints/{endpoint_id}/")
        return EndpointResponseDTO(**data)

    async def list_endpoints(self) -> List[EndpointResponseDTO]:
        data = await self._get("/api/v1/endpoints/")
        return [EndpointResponseDTO.model_validate(item) for item in data]

    async def delete_endpoint(self, endpoint_id: str) -> bool:
        await self._delete(f"/api/v1/endpoints/{endpoint_id}/")
        return True

    # -------------------- SecurityPolicy Methods --------------------
    async def create_security_policy(self, policy: SecurityPolicyDTO) -> Result[SecurityPolicyResponseDTO, CreationError]:
        try:
            payload = policy.model_dump(by_alias=True)
            data = await self._post("/api/v1/security-policies/", payload)
            return Ok(SecurityPolicyResponseDTO(**data))
        except Exception as e:
            return Err(CreationError("security_policy", policy.sp_id, e))

    async def get_security_policy(self, sp_id: str) -> SecurityPolicyResponseDTO:
        data = await self._get(f"/api/v1/security-policies/{sp_id}/")
        return SecurityPolicyResponseDTO(**data)

    async def list_security_policies(self) -> List[SecurityPolicyResponseDTO]:
        data = await self._get("/api/v1/security-policies/")
        return [SecurityPolicyResponseDTO(**item) for item in data]

    async def delete_security_policy(self, sp_id: str) -> bool:
        await self._delete(f"/api/v1/security-policies/{sp_id}/")
        return True

    # -------------------- Role Methods --------------------
    async def create_role(self, role: RoleCreateDTO) -> Result[RoleResponseDTO, CreationError]:
        try:
            payload = role.model_dump(by_alias=True)
            data = await self._post("/api/v1/roles/", payload)
            return RoleResponseDTO(**data)
        except Exception as e:
            return Err(CreationError("role", role.role_id, e))

    async def get_role(self, role_id: str) -> RoleResponseDTO:
        data = await self._get(f"/api/v1/roles/{role_id}/")
        return RoleResponseDTO(**data)

    async def list_roles(self) -> List[RoleResponseDTO]:
        data = await self._get("/api/v1/roles/")
        return [RoleResponseDTO(**item) for item in data]

    async def delete_role(self, role_id: str) -> bool:
        await self._delete(f"/api/v1/roles/{role_id}/")
        return True

    # -------------------- FunctionState Methods --------------------
    async def list_function_states(self) -> List[FunctionStateResponseDTO]:
        data = await self._get("/api/v1/function-states/")
        return [FunctionStateResponseDTO(**item) for item in data]

    # -------------------- FunctionResult Methods --------------------
    async def list_function_results(self) -> List[FunctionResultResponseDTO]:
        data = await self._get("/api/v1/function-results/")
        return [FunctionResultResponseDTO(**item) for item in data]

    # -------------------- EndpointState Methods --------------------
    async def list_endpoint_states(self) -> List[EndpointStateResponseDTO]:
        data = await self._get("/api/v1/endpoint-states/")
        return [EndpointStateResponseDTO(**item) for item in data]

    async def get_endpoint_state(self, state_id: str) -> EndpointStateResponseDTO:
        data = await self._get(f"/api/v1/endpoint-states/{state_id}/")
        return EndpointStateResponseDTO(**data)

    async def delete_endpoint_state(self, state_id: str) -> bool:
        await self._delete(f"/api/v1/endpoint-states/{state_id}/")
        return True

    # -------------------- Core HTTP Methods --------------------
    async def _get(self, path: str, headers: Dict[str, str] = {}) -> Any:
        url = f"{self.base_url}{path}"
        full_headers = {**self.headers, **headers}
        t1 = time.time()
        async with httpx.AsyncClient(headers=full_headers, follow_redirects=True) as client:
            response = await client.get(url)
        L.info({
            "event": "GET", 
            "path": path, 
            "status": response.status_code, 
            "elapsed": round(time.time() - t1, 3)
        })
        return await self._handle_response(response)

    async def _post(self, path: str, payload: Dict[str, Any], headers: Dict[str, str] = {}) -> Any:
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
        L.info({
            "event": "PUT",
            "path": path,
            "status": response.status_code,
            "elapsed": round(time.time() - t1, 3)
        })
        return await self._handle_response(response)

    async def _delete(self, path: str, headers: Dict[str, str] = {}) -> Any:
        url = f"{self.base_url}{path}"
        full_headers = {**self.headers, **headers}
        t1 = time.time()
        async with httpx.AsyncClient(headers=full_headers, follow_redirects=True) as client:
            response = await client.delete(url)
        L.info({
            "event": "DELETE",
            "path": path,
            "status": response.status_code,
            "elapsed": round(time.time() - t1, 3)
        })
        return await self._handle_response(response)