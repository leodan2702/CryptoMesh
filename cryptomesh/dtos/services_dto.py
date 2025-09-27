from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from cryptomesh.models import ServiceModel
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
import uuid

# -------------------------------
# DTO para creación de servicios
# -------------------------------
class ServiceCreateDTO(BaseModel):
    """
    DTO para recibir datos de creación de un servicio.
    Incluye recursos, microservicios iniciales y política asociada.
    """
    name: str
    security_policy: str  # Política de seguridad aplicada
    resources: ResourcesDTO  # Recursos asignados al servicio
    policy_id: Optional[str] = None  # ID de la política YAML

    def to_model(self, service_id: Optional[str] = None) -> ServiceModel:
        """
        Convierte un DTO de creación en un ServiceModel listo para persistir.
        """
        return ServiceModel(
            service_id=service_id or str(uuid.uuid4()),
            name=self.name,
            security_policy=self.security_policy,
            resources=self.resources.to_model(),
            created_at=datetime.utcnow(),
            policy_id=self.policy_id
        )

    @staticmethod
    def from_model(model: ServiceModel) -> "ServiceCreateDTO":
        """
        Convierte un ServiceModel a un DTO de creación.
        """
        return ServiceCreateDTO(
            name=model.name,
            security_policy=model.security_policy,
            resources=ResourcesDTO.from_model(model.resources),
            policy_id=model.policy_id
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class ServiceResponseDTO(BaseModel):
    """
    DTO que se envía al cliente al consultar servicios.
    Incluye únicamente información segura y útil.
    """
    service_id: str
    name: str
    resources: ResourcesDTO
    security_policy: str

    @staticmethod
    def from_model(model: ServiceModel) -> "ServiceResponseDTO":
        """
        Convierte un ServiceModel en un DTO de respuesta segura.
        """
        return ServiceResponseDTO(
            service_id=model.service_id,
            name=model.name,
            resources=ResourcesDTO.from_model(model.resources),
            security_policy=model.security_policy
        )


# -------------------------------
# DTO para actualización de servicios
# -------------------------------
class ServiceUpdateDTO(BaseModel):
    """
    DTO para actualizar parcialmente un servicio.
    Solo los campos enviados se aplicarán sobre el modelo existente.
    """
    name: Optional[str] = None
    resources: Optional[ResourcesUpdateDTO] = None
    security_policy: Optional[str] = None

    @staticmethod
    def apply_updates(dto: "ServiceUpdateDTO", model: ServiceModel) -> ServiceModel:
        """
        Aplica los cambios del DTO sobre un ServiceModel existente.
        Convierte los DTOs incrustados a modelos internos antes de asignar.
        """
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "resources" and value is not None:
                resource_dto = ResourcesUpdateDTO(**value)
                model.resources = ResourcesUpdateDTO.apply_updates(resource_dto, model.resources)
            else:
                setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: ServiceModel) -> "ServiceUpdateDTO":
        """
        Convierte un ServiceModel en un DTO de actualización.
        """
        return ServiceUpdateDTO(
            name=model.name,
            resources=ResourcesUpdateDTO.from_model(model.resources),
            security_policy= model.security_policy
        )
