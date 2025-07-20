from datetime import datetime
from pydantic import BaseModel, Field
from cryptomesh_client.models.resources import ResourcesModel

class EndpointModel(BaseModel):
    endpoint_id: str
    name: str
    image: str
    resources: ResourcesModel  # recurso incrustado
    security_policy: str       # sp_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    policy_id: str