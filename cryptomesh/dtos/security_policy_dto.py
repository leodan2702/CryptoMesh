from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from cryptomesh.models import SecurityPolicyModel
import uuid

# -------------------------------
# DTO base para seguridad
# -------------------------------
class SecurityPolicyDTO(BaseModel):
    """
    DTO centralizado para políticas de seguridad.
    Se utiliza para creación, actualización y respuesta.
    """
    sp_id: Optional[str] = None
    roles: List[str]
    requires_authentication: bool

    @field_validator("roles")
    def roles_must_not_be_empty(cls, v):
        if not v or not all(role.strip() for role in v):
            raise ValueError("Roles list cannot be empty or contain blank roles")
        return v

    def to_model(self) -> SecurityPolicyModel:
        return SecurityPolicyModel(
            sp_id=self.sp_id or str(uuid.uuid4()),
            roles=self.roles,
            requires_authentication=self.requires_authentication,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def from_model(model: SecurityPolicyModel) -> "SecurityPolicyDTO":
        return SecurityPolicyDTO(
            sp_id=model.sp_id,
            roles=model.roles,
            requires_authentication=model.requires_authentication
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class SecurityPolicyResponseDTO(BaseModel):
    sp_id: str
    roles: List[str]
    requires_authentication: bool

    @staticmethod
    def from_model(model: SecurityPolicyModel) -> "SecurityPolicyResponseDTO":
        """
        Convierte un SecurityPolicyModel en un DTO de respuesta segura.
        """
        return SecurityPolicyResponseDTO(
            sp_id=model.sp_id,
            roles=model.roles,
            requires_authentication=model.requires_authentication,
        )


# -------------------------------
# DTO para actualización de políticas de seguridad
# -------------------------------
class SecurityPolicyUpdateDTO(BaseModel):
    roles: Optional[List[str]] = None
    requires_authentication: Optional[bool] = None

    @field_validator("roles")
    def roles_if_present_must_not_be_empty(cls, v):
        if v is not None and (not v or not all(role.strip() for role in v)):
            raise ValueError("Roles list cannot be empty or contain blank roles")
        return v

    @staticmethod
    def apply_updates(dto: "SecurityPolicyUpdateDTO", model: SecurityPolicyModel) -> SecurityPolicyModel:
        """
        Aplica los cambios del DTO sobre un SecurityPolicyModel existente.
        Solo actualiza los campos enviados por el cliente.
        """
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: SecurityPolicyModel) -> "SecurityPolicyUpdateDTO":
        return SecurityPolicyUpdateDTO(
            roles=model.roles,
            requires_authentication=model.requires_authentication
        )
