from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from cryptomesh_client.models.resources import ResourcesModel

class ServiceModel(BaseModel):
    service_id: str
    security_policy: str  # sp_id
    microservices: List[str]  # Lista de microservice_id
    resources: ResourcesModel
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: str