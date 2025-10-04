from datetime import datetime,timezone
from pydantic import BaseModel, Field, ConfigDict, validator, field_validator
from typing import List, Dict, Optional,Any
from cryptomesh.validators.validators import (
    ServiceNameStr,
    MicroserviceNameStr,
    RoleNameStr,
    EndpointNameStr,
    SecurityPolicyNameStr,
    paramNameStr,
    FunctionNameStr,
    AxoNameStr
)
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
    model_config = ConfigDict(validate_assignment=True)
    role_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: RoleNameStr
    description: str
    permissions: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SecurityPolicyModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    sp_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: SecurityPolicyNameStr
    roles: List[str]  # Referencias a RoleModel
    requires_authentication: bool
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class EndpointModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    endpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: EndpointNameStr
    image: str
    resources: ResourcesModel # resource_id
    security_policy: str  # sp_id
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    policy_id: Optional[str] = None #reference to yaml policy
    active_object_id: Optional[str] = None
    envs:Optional[Dict[str,str]] = Field(default={})

class EndpointStateModel(BaseModel):
    state_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    endpoint_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

class ServiceModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    service_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: ServiceNameStr
    security_policy: str # sp_id
    resources: ResourcesModel  # resource_id
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    policy_id: Optional[str] = None

class MicroserviceModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    microservice_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: MicroserviceNameStr
    service_id: str
    resources: ResourcesModel  # resource_id
    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))
    policy_id: Optional[str] = None


class ParameterSpec(BaseModel):
    """Esquema de un parámetro de función"""
    model_config = ConfigDict(validate_assignment=True)
    name: paramNameStr                       # nombre del parámetro
    type: str                           # tipo esperado (str, int, DiGraph, etc.)
    description: Optional[str] = None   # descripción opcional
    required: bool = True               # si es obligatorio
    default: Optional[Any] = None       # valor por defecto

class FunctionModel(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    function_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: FunctionNameStr                         # ej. "run"
    init_params: List[ParameterSpec] = Field(default_factory=list)  # kwargs de __init__
    call_params: List[ParameterSpec] = Field(default_factory=list)   # kwargs de la función
    
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    

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
    axo_microservice_id: str
    
    axo_dependencies: List[str] = Field(default_factory=list)
    
    axo_uri: Optional[str] = None
    axo_alias: AxoNameStr
    axo_code: Optional[str] = None
    axo_schema: Optional[Dict[str, object]] = Field(
        default=None,
        description="JSON schema of constructor args and methods extracted from axo_code"
    )
    functions: List[FunctionModel] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda:datetime.now(timezone.utc))

    @field_validator("axo_version")
    @classmethod
    def validate_version(cls, v):
        if v < 0:
            raise ValueError("Version must be >= 0")
        return v

    @field_validator("functions", mode="before")
    @classmethod
    def validate_functions(cls, v):
        if not v:
            return []
        return [
            f if isinstance(f, FunctionModel) else FunctionModel(**f)
            for f in v
        ]


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





