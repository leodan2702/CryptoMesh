from cryptomesh.dtos.endpoints_dto import (EndpointCreateDTO, EndpointResponseDTO, EndpointUpdateDTO)
from cryptomesh.dtos.function_result_dto import FunctionResultCreateDTO, FunctionResultResponseDTO, FunctionResultUpdateDTO
from cryptomesh.dtos.function_state_dto import FunctionStateCreateDTO, FunctionStateResponseDTO, FunctionStateUpdateDTO
from cryptomesh.dtos.functions_dto import FunctionCreateDTO, FunctionResponseDTO, FunctionUpdateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO, SecurityPolicyResponseDTO, SecurityPolicyUpdateDTO
from cryptomesh.dtos.microservices_dto import MicroserviceCreateDTO, MicroserviceResponseDTO, MicroserviceUpdateDTO
from cryptomesh.dtos.role_dto import RoleCreateDTO, RoleResponseDTO, RoleUpdateDTO

from cryptomesh.dtos.services_dto import ServiceCreateDTO, ServiceResponseDTO, ServiceUpdateDTO
from cryptomesh.dtos.storage_dto import StorageDTO, StorageUpdateDTO

from cryptomesh.dtos.endpoint_state_dto import EndpointStateCreateDTO, EndpointStateResponseDTO, EndpointStateUpdateDTO

from pydantic import BaseModel,Field
from typing import List,Dict,Optional


class ParameterSpecDTO(BaseModel):
    name: str
    type: str
    description: Optional[str] = Field(default="No description.")
    required: bool = Field(default=True)
    default: Optional[str] = Field(default=None)

class SchemaDTO(BaseModel):
    class_name: str
    init: List[ParameterSpecDTO]
    methods: Dict[str, List[ParameterSpecDTO]]
