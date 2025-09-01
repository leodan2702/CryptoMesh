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
    async def create_function(self, function: FunctionCreateDTO) -> Result[FunctionResponseDTO, Exception]:
        payload = function.model_dump(by_alias=True)
        data = await self._post("/api/v1/functions/", payload)
        if data.is_ok:
            return Ok(FunctionResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def get_function(self, function_id: str) -> Result[FunctionResponseDTO, Exception]:
        data = await self._get(f"/api/v1/functions/{function_id}/")
        if data.is_ok:
            return Ok(FunctionResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def list_functions(self) -> List[FunctionResponseDTO]:
        data = await self._get("/api/v1/functions/")
        return [FunctionResponseDTO.model_validate(item) for item in data]

    async def update_function(self, function_id: str, function: FunctionUpdateDTO) -> Result[FunctionResponseDTO, Exception]:
        payload = function.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/functions/{function_id}/", payload)
        if data.is_ok:
            return Ok(FunctionResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
    
    async def delete_function(self, function_id: str) -> Result[bool, Exception]:
        try:
            data = await self._delete(f"/api/v1/functions/{function_id}/")
            return Ok(True)
        except Exception as e:
            return Err(e)

    # -------------------- Service Methods --------------------
    async def create_service(self, service: ServiceCreateDTO) -> Result[ServiceResponseDTO, Exception]:
        payload = service.model_dump(by_alias=True)
        data = await self._post("/api/v1/services/", payload)
        if data.is_ok:
            return Ok(ServiceResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def get_service(self, service_id:str) -> Result[ServiceResponseDTO, Exception]:
        data = await self._get(f"/api/v1/services/{service_id}/")
        if data.is_ok:
            return Ok(ServiceResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def list_services(self) -> List[ServiceResponseDTO]:
        data = await self._get("/api/v1/services/")
        return [ServiceResponseDTO(**item) for item in data]

    async def update_service(self, service_id: str, service: ServiceUpdateDTO) -> Result[ServiceResponseDTO, Exception]:
        payload = service.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/services/{service_id}/", payload)
        if data.is_ok:
            return Ok(ServiceResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
    
    async def delete_service(self, service_id: str) -> Result[bool, Exception]:
        try:
            await self._delete(f"/api/v1/services/{service_id}/")
            return Ok(True)
        except Exception as e:
            return Err(e)

    # -------------------- Microservice Methods --------------------
    async def create_microservice(self, microservice: MicroserviceCreateDTO) -> Result[MicroserviceResponseDTO, Exception]:
        payload = microservice.model_dump(by_alias=True)
        data = await self._post("/api/v1/microservices/", payload)
        if data.is_ok:
            return Ok(MicroserviceResponseDTO.model_validate(data.unwrap()))    
        return Err(data.unwrap_err())

    async def get_microservice(self, microservice_id: str) -> Result[MicroserviceResponseDTO, Exception]:
        data = await self._get(f"/api/v1/microservices/{microservice_id}/")
        if data.is_ok:
            return Ok(MicroserviceResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def list_microservices(self) -> List[MicroserviceResponseDTO]:
        data = await self._get("/api/v1/microservices/")
        return [MicroserviceResponseDTO.model_validate(item) for item in data]

    async def update_microservice(self, microservice_id: str, microservice: MicroserviceUpdateDTO) -> Result[MicroserviceResponseDTO, Exception]:
        payload = microservice.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/microservices/{microservice_id}/", payload)
        if data.is_ok:
            return Ok(MicroserviceResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def delete_microservice(self, microservice_id: str) -> Result[bool, Exception]:
        try:
            await self._delete(f"/api/v1/microservices/{microservice_id}/")
            return Ok (True)
        except Exception as e:
            return Err(e)

    # -------------------- Endpoint Methods --------------------
    async def create_endpoint(self, endpoint: EndpointCreateDTO) -> Result[EndpointResponseDTO,Exception]:
        payload = endpoint.model_dump(by_alias=True)
        data = await self._post("/api/v1/endpoints/", payload)
        if data.is_ok:
            return Ok(EndpointResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
    
    async def get_endpoint(self, endpoint_id: str) -> Result[EndpointResponseDTO, Exception]:
        data = await self._get(f"/api/v1/endpoints/{endpoint_id}/")
        if data.is_ok:
            return Ok(EndpointResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
    

    async def list_endpoints(self) -> List[EndpointResponseDTO]:
        data = await self._get("/api/v1/endpoints/")
        return [EndpointResponseDTO.model_validate(item) for item in data]

    async def update_endpoint(self, endpoint_id: str, endpoint: EndpointUpdateDTO) -> Result[EndpointResponseDTO, Exception]:
        payload = endpoint.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/endpoints/{endpoint_id}/", payload)
        if data.is_ok:
            return Ok(EndpointResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def delete_endpoint(self, endpoint_id: str) -> Result[bool, Exception]:
        try:
            await self._delete(f"/api/v1/endpoints/{endpoint_id}/")
            return Ok(True)
        except Exception as e:
            return Err(e)

    # -------------------- SecurityPolicy Methods --------------------
    async def create_security_policy(self, policy: SecurityPolicyDTO) -> Result[SecurityPolicyResponseDTO, Exception]:
        payload = policy.model_dump(by_alias=True)
        data = await self._post("/api/v1/security-policies/", payload)
        if data.is_ok:
            return Ok(SecurityPolicyResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def get_security_policy(self, sp_id: str) -> Result[SecurityPolicyResponseDTO, Exception]:
        data = await self._get(f"/api/v1/security-policies/{sp_id}/")
        if data.is_ok:
            return Ok(SecurityPolicyResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def list_security_policies(self) -> List[SecurityPolicyResponseDTO]:
        data = await self._get("/api/v1/security-policies/")
        return [SecurityPolicyResponseDTO.model_validate(item) for item in data]

    async def update_security_policy(self, sp_id: str, policy: SecurityPolicyUpdateDTO) -> Result[SecurityPolicyResponseDTO, Exception]:
        payload = policy.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/security-policies/{sp_id}/", payload)
        if data.is_ok:
            return Ok(SecurityPolicyResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def delete_security_policy(self, sp_id: str) -> Result[bool, Exception]:
        try:
            await self._delete(f"/api/v1/security-policies/{sp_id}/")
            return Ok(True)
        except Exception as e:
            return Err(e)

    # -------------------- Role Methods --------------------
    async def create_role(self, role: RoleCreateDTO) -> Result[RoleResponseDTO, Exception]:
        payload = role.model_dump(by_alias=True)
        data = await self._post("/api/v1/roles/", payload)
        if data.is_ok:
            return Ok(RoleResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())


    async def get_role(self, role_id: str) -> Result[RoleResponseDTO, Exception]:
        data = await self._get(f"/api/v1/roles/{role_id}/")
        if data.is_ok:
            return Ok(RoleResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def list_roles(self) -> List[RoleResponseDTO]:
        data = await self._get("/api/v1/roles/")
        return [RoleResponseDTO.model_validate(item) for item in data]

    async def update_role(self, role_id: str, role: RoleUpdateDTO) -> Result[RoleResponseDTO, Exception]:
        payload = role.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/roles/{role_id}/", payload)
        if data.is_ok:
            return Ok(RoleResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def delete_role(self, role_id: str) -> Result[bool, Exception]:
        try:
            await self._delete(f"/api/v1/roles/{role_id}/")
            return Ok(True)
        except Exception as e:
            return Err(e)

    # -------------------- FunctionState Methods --------------------
    async def create_function_state(self, state: FunctionStateCreateDTO) -> Result[FunctionStateResponseDTO, Exception]:
        payload = state.model_dump(by_alias=True)
        data = await self._post("/api/v1/function-states/", payload)
        if data.is_ok:
            return Ok(FunctionStateResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def get_function_state(self, state_id: str) -> Result[FunctionStateResponseDTO, Exception]:
        data = await self._get(f"/api/v1/function-states/{state_id}/")
        if data.is_ok:
            return Ok(FunctionStateResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
    
    async def list_function_states(self) -> List[FunctionStateResponseDTO]:
        data = await self._get("/api/v1/function-states/")
        return [FunctionStateResponseDTO.model_validate(item) for item in data]

    async def update_function_state(self, state_id: str, state: FunctionStateUpdateDTO) -> Result[FunctionStateResponseDTO, Exception]:
        payload = state.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/function-states/{state_id}/", payload)
        if data.is_ok:
            return Ok(FunctionStateResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def delete_function_state(self, state_id: str) -> Result[bool, Exception]:
        try:
            await self._delete(f"/api/v1/function-states/{state_id}/")
            return Ok(True)
        except Exception as e:
            return Err(e)

    # -------------------- FunctionResult Methods --------------------
    async def create_function_result(self, result: FunctionResultCreateDTO) -> Result[FunctionResultResponseDTO, Exception]:
        payload = result.model_dump(by_alias=True)
        data = await self._post("/api/v1/function-results/", payload)
        if data.is_ok:
            return Ok(FunctionResultResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def get_function_result(self, result_id: str) -> Result[FunctionResultResponseDTO, Exception]:
        data = await self._get(f"/api/v1/function-results/{result_id}/")
        if data.is_ok:
            return Ok(FunctionResultResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
        
    async def list_function_results(self) -> List[FunctionResultResponseDTO]:
        data = await self._get("/api/v1/function-results/")
        return [FunctionResultResponseDTO.model_validate(item) for item in data]

    async def update_function_result(self, result_id: str, result: FunctionResultUpdateDTO) -> Result[FunctionResultResponseDTO, Exception]:
        payload = result.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/function-results/{result_id}/", payload)
        if data.is_ok:
            return Ok(FunctionResultResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def delete_function_result(self, result_id: str) -> Result[bool, Exception]:
        try:
            await self._delete(f"/api/v1/function-results/{result_id}/")
            return Ok(True)
        except Exception as e:
            return Err(e)

    # -------------------- EndpointState Methods --------------------
    async def create_endpoint_state(self, state: EndpointStateCreateDTO) -> Result[EndpointStateResponseDTO, Exception]:
        payload = state.model_dump(by_alias=True)
        data = await self._post("/api/v1/endpoint-states/", payload)
        if data.is_ok:
            return Ok(EndpointStateResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
    
    async def list_endpoint_states(self) -> List[EndpointStateResponseDTO]:
        data = await self._get("/api/v1/endpoint-states/")
        return [EndpointStateResponseDTO.model_validate(item) for item in data]

    async def get_endpoint_state(self, state_id: str) -> Result[EndpointStateResponseDTO, Exception]:
        data = await self._get(f"/api/v1/endpoint-states/{state_id}/")
        if data.is_ok:
            return Ok(EndpointStateResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())
    
    async def update_endpoint_state(self, state_id: str, state: EndpointStateUpdateDTO) -> Result[EndpointStateResponseDTO, Exception]:
        payload = state.model_dump(by_alias=True, exclude_none=True)
        data = await self._put(f"/api/v1/endpoint-states/{state_id}/", payload)
        if data.is_ok:
            return Ok(EndpointStateResponseDTO.model_validate(data.unwrap()))
        return Err(data.unwrap_err())

    async def delete_endpoint_state(self, state_id: str) -> Result[bool, Exception]:
        try:
            await self._delete(f"/api/v1/endpoint-states/{state_id}/")
            return Ok(True)
        except Exception as e:
            return Err(e)

    # -------------------- Core HTTP Methods --------------------
    async def _get(self, path: str, headers: Dict[str, str] = {}) -> Result[Any, Exception]:
        try:
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

            data = await self._handle_response(response)
            return Ok(data)

        except Exception as e:
            return Err(e)


    async def _post(self, path: str, payload: Dict[str, Any], headers: Dict[str, str] = {}) -> Result[Any, Exception]:
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


    async def _put(self, path: str, payload: Any, headers: Dict[str, str] = {}) -> Result[Any, Exception]:
        try:
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

            data = await self._handle_response(response)
            return Ok(data)

        except Exception as e:
            return Err(e)


    async def _delete(self, path: str, headers: Dict[str, str] = {}) -> Result[Any, Exception]:
        try:
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

            data = await self._handle_response(response)
            return Ok(data)

        except Exception as e:
            return Err(e)
