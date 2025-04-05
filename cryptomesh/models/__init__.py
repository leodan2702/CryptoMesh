from typing import Dict, List, Optional
from pydantic import BaseModel
from pydantic import BaseModel, Field

class SecurityPolicy(BaseModel):
    roles: List[str]
    requires_authentication: Optional[bool] = False

class Resource(BaseModel):
    ram: str
    cpu: int

class StoragePath(BaseModel):
    path: str
    bucket_id: Optional[str] = None

class Storage(BaseModel):
    capacity: str
    source: StoragePath
    sink: StoragePath

class FunctionModel(BaseModel):
    image: str
    resources: Resource
    storage: Storage

class MicroserviceModel(BaseModel):
    security_policy: Optional[SecurityPolicy]
    resources: Optional[Resource]
    functions: Dict[str, FunctionModel]

class ServiceModel(BaseModel):
    security_policy: SecurityPolicy
    microservices: Dict[str, MicroserviceModel]

class ConnectionModel(BaseModel):
    from_: str = Field(..., alias="from")
    to: List[str]
    condition: str
    event: Optional[str] = None 

class PolicyModel(BaseModel):
    cryptomesh: str
    services: Dict[str, ServiceModel]
    connections: List[ConnectionModel]





