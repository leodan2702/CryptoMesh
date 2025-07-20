# cryptomesh_client/models/function_result.py

from pydantic import BaseModel, Field
from typing import Dict
from datetime import datetime

class FunctionResultModel(BaseModel):
    state_id: str
    function_id: str
    metadata: Dict[str, str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
