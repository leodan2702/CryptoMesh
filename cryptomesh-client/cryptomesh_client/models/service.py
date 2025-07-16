from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from cryptomesh_client.models.resources import ResourcesModel
from cryptomesh_client.models.security_policy import SecurityPolicyModel


class ServiceModel(BaseModel):
    service_id: str
    security_policy: SecurityPolicyModel  # sp_id
    microservices: List[str]  # Lista de microservice_id
    resources: ResourcesModel
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: Optional[str] = None