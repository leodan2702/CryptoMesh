from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional
from cryptomesh_client.models.resources import ResourcesModel
from cryptomesh_client.models.security_policy import SecurityPolicyModel


class EndpointModel(BaseModel):
    endpoint_id: str
    name: str
    image: str
    resources: ResourcesModel  # recurso incrustado
    security_policy: SecurityPolicyModel       # sp_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: Optional[str] = None