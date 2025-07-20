from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict
from cryptomesh.cryptomesh_client.models.resources import ResourcesModel
from cryptomesh.cryptomesh_client.models.storage import StorageModel

class FunctionModel(BaseModel):
    function_id: str
    microservice_id: str
    image: str
    resources: ResourcesModel
    storage: StorageModel
    endpoint_id: str
    deployment_status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: str