from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class RoleModel(BaseModel):
    role_id: str
    name: str
    description: str
    permissions: List[str]
    created_at: datetime = Field(default_factory=datetime.utcnow)
