from datetime import datetime
from typing import List
from pydantic import BaseModel, Field

class SecurityPolicyModel(BaseModel):
    sp_id: str
    roles: List[str]  # Referencias a RoleModel
    requires_authentication: bool
    created_at: datetime = Field(default_factory=datetime.utcnow)