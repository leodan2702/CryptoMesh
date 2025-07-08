from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Dict

class ResourcesModel(BaseModel):
    cpu: int
    ram: str
    
class StorageModel(BaseModel):
    capacity: str
    storage_id: str
    source_path: str
    sink_path: str

class RoleModel(BaseModel):
    role_id: str
    name: str
    description: str
    permissions: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SecurityPolicyModel(BaseModel):
    sp_id: str
    roles: List[str]  # Referencias a RoleModel
    requires_authentication: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EndpointModel(BaseModel):
    endpoint_id: str
    name: str
    image: str
    resources: ResourcesModel # resource_id
    security_policy: str  # sp_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: str

class EndpointStateModel(BaseModel):
    state_id: str
    endpoint_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ServiceModel(BaseModel):
    service_id: str
    security_policy: str # sp_id
    microservices: List[str]  # Lista de microservice_id
    resources: ResourcesModel  # resource_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: str

class MicroserviceModel(BaseModel):
    microservice_id: str
    service_id: str
    functions: List[str]  # Lista de function_id
    resources: ResourcesModel  # resource_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: str

class FunctionModel(BaseModel):
    function_id: str
    microservice_id: str
    image: str
    resources: ResourcesModel  #INCRUSTADO
    storage: StorageModel      #INCRUSTADO
    endpoint_id: str
    deployment_status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: str

class FunctionStateModel(BaseModel):
    state_id: str
    function_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class FunctionResultModel(BaseModel):
    state_id: str
    function_id: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)





