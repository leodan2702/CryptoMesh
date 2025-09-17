from datetime import datetime,timezone
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uuid

class SummonerParams(BaseModel):
    ip_addr:Optional[str] = "localhost"
    port: Optional[int] = 15000
    protocol:Optional[str] = "http"
    api_version:Optional[int] = 3
    mode:Optional[str] ="docker"


class ResourcesModel(BaseModel):
    cpu: int
    ram: str
    
class StorageModel(BaseModel):
    capacity: str
    source_path: str
    sink_path: str

class RoleModel(BaseModel):
    role_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    permissions: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SecurityPolicyModel(BaseModel):
    sp_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    roles: List[str]  # Referencias a RoleModel
    requires_authentication: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EndpointModel(BaseModel):
    endpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    image: str
    resources: ResourcesModel # resource_id
    security_policy: SecurityPolicyModel  # sp_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    policy_id: Optional[str] = None #reference to yaml policy
    envs:Optional[Dict[str,str]] = Field(default={})

class EndpointStateModel(BaseModel):
    state_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    endpoint_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

class ServiceModel(BaseModel):
    service_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    security_policy: SecurityPolicyModel # sp_id
    microservices: List[str]  # Lista de microservice_id
    resources: ResourcesModel  # resource_id
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    policy_id: str

class MicroserviceModel(BaseModel):
    microservice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str
    functions: List[str]  # Lista de function_id
    resources: ResourcesModel  # resource_id
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    policy_id: str

class FunctionModel(BaseModel):
    function_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    microservice_id: str
    image: str
    resources: ResourcesModel  #INCRUSTADO
    storage: StorageModel      #INCRUSTADO
    endpoint_id: str
    deployment_status: str
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    policy_id: str

class FunctionStateModel(BaseModel):
    state_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    function_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

class FunctionResultModel(BaseModel):
    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    function_id: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))





