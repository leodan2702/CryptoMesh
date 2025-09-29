from pydantic import BaseModel
from typing import List, Optional, Any

class ParameterDTO(BaseModel):
    name: str
    type: Optional[str] = None
    description: Optional[str] = None
    required: bool = False
    default: Optional[Any] = None

class FunctionHierarchyDTO(BaseModel):
    function_id: str
    name: str
    init_params: List[ParameterDTO] = []
    call_params: List[ParameterDTO] = []

class ActiveObjectHierarchyDTO(BaseModel):
    active_object_id: str
    object_name: str
    alias: Optional[str] = None
    version: int
    functions: List[FunctionHierarchyDTO] = []

class MicroserviceHierarchyDTO(BaseModel):
    microservice_id: str
    microservice_name: str
    active_objects: List[ActiveObjectHierarchyDTO] = []

class ServiceHierarchyDTO(BaseModel):
    service_id: str
    service_name: str
    microservices: List[MicroserviceHierarchyDTO] = []
