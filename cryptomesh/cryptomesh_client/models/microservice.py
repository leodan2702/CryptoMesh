from datetime import datetime
from pydantic import BaseModel, Field
from typing import List
from cryptomesh.cryptomesh_client.models.resources import ResourcesModel

class MicroserviceModel(BaseModel):
    microservice_id: str
    service_id: str
    functions: List[str]  # Lista de function_id
    resources: ResourcesModel
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: str