# cryptomesh_client/models/endpoint_state.py

from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime

class EndpointStateModel(BaseModel):
    state_id: str
    endpoint_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
