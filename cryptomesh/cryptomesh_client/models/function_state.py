# cryptomesh_client/models/function_state.py

from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime

class FunctionStateModel(BaseModel):
    state_id: str
    function_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
