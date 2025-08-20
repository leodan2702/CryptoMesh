from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from cryptomesh.models import RoleModel
import uuid

# -------------------------------
# DTO para creación de roles
# -------------------------------
class RoleCreateDTO(BaseModel):
    """
    DTO para recibir datos de creación de un rol.
    Incluye nombre, descripción y permisos asociados.
    """
    name: str
    description: str
    permissions: List[str]

    def to_model(self, role_id: Optional[str] = None) -> RoleModel:
        """
        Convierte un DTO de creación en un RoleModel listo para persistir.
        Se puede pasar un role_id si se desea asignar manualmente.
        """
        return RoleModel(
            role_id=role_id or str(uuid.uuid4()),
            name=self.name,
            description=self.description,
            permissions=self.permissions,
            created_at=datetime.utcnow()
        )

    @staticmethod
    def from_model(model: RoleModel) -> "RoleCreateDTO":
        """
        Convierte un RoleModel a un DTO de creación.
        Útil para pruebas o serialización bidireccional.
        """
        return RoleCreateDTO(
            name=model.name,
            description=model.description,
            permissions=model.permissions
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class RoleResponseDTO(BaseModel):
    """
    DTO que se envía al cliente al consultar roles.
    Contiene información segura y relevante.
    """
    role_id: str
    name: str
    description: str
    permissions: List[str]

    @staticmethod
    def from_model(model: RoleModel) -> "RoleResponseDTO":
        """
        Convierte un RoleModel en un DTO de respuesta segura.
        """
        return RoleResponseDTO(
            role_id=model.role_id,
            name=model.name,
            description=model.description,
            permissions=model.permissions,
        )


# -------------------------------
# DTO para actualización de roles
# -------------------------------
class RoleUpdateDTO(BaseModel):
    """
    DTO para actualizar parcialmente un rol.
    Solo los campos enviados se aplicarán sobre el modelo existente.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

    @staticmethod
    def apply_updates(dto: "RoleUpdateDTO", model: RoleModel) -> RoleModel:
        """
        Aplica los cambios del DTO sobre un RoleModel existente.
        Solo actualiza los campos enviados por el cliente.
        """
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: RoleModel) -> "RoleUpdateDTO":
        """
        Convierte un RoleModel en un DTO de actualización.
        """
        return RoleUpdateDTO(
            name=model.name,
            description=model.description,
            permissions=model.permissions
        )
