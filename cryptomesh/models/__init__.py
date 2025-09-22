from datetime import datetime,timezone
from pydantic import BaseModel, Field, ConfigDict, validator, field_validator
from typing import List, Dict, Optional
import uuid

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
    name: str
    roles: List[str]  # Referencias a RoleModel
    requires_authentication: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EndpointModel(BaseModel):
    endpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    image: str
    resources: ResourcesModel # resource_id
    security_policy: str  # sp_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    policy_id: Optional[str] = None #reference to yaml policy
    active_object_id: Optional[str] = None

class EndpointStateModel(BaseModel):
    state_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    endpoint_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

class ServiceModel(BaseModel):
    service_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    security_policy: str # sp_id
    microservices: List[str]  # Lista de microservice_id
    resources: ResourcesModel  # resource_id
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    policy_id: Optional[str] = None

class MicroserviceModel(BaseModel):
    microservice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    service_id: str
    functions: List[str]  # Lista de function_id
    resources: ResourcesModel  # resource_id
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    policy_id: Optional[str] = None

class FunctionModel(BaseModel):
    function_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    microservice_id: str
    image: str
    resources: ResourcesModel  #INCRUSTADO
    storage: StorageModel      #INCRUSTADO
    endpoint_id: str
    deployment_status: str
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    policy_id: Optional[str] = None

class ActiveObjectModel(BaseModel):
    """Serializable metafata stored alongside every active object"""
    model_config = ConfigDict(validate_assignment = True)
    active_object_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    #class-level defaults (paths can be overriden via env-vars)
    path: Optional[str] = "/axo/data"
    source_path: Optional[str] = "/axo/source"
    sink_path: Optional[str] = "/axo/sink"

    #stored fields
    axo_is_read_only: bool = False

    axo_key: str = Field(default_factory = lambda: str(uuid.uuid4()))
    axo_bucket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    axo_source_bucket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    axo_sink_bucket_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    axo_module: str
    axo_class_name: str
    axo_version: int = 0

    axo_endpoint_id: Optional[str] = None
    axo_dependencies: List[str] = Field(default_factory=list)
    
    axo_uri: Optional[str] = None
    axo_alias: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

    @field_validator("axo_version")
    @classmethod
    def validate_version(cls, v):
        if v < 0:
            raise ValueError("Version must be >= 0")
        return v


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





