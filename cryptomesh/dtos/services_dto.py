from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from cryptomesh.models import ServiceModel
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO, SecurityPolicyResponseDTO, SecurityPolicyUpdateDTO
import uuid

# -------------------------------
# DTO para creación de servicios
# -------------------------------
class ServiceCreateDTO(BaseModel):
    """
    DTO para recibir datos de creación de un servicio.
    Incluye recursos, microservicios iniciales y política asociada.
    """
    security_policy: SecurityPolicyDTO  # Política de seguridad aplicada
    microservices: Optional[List[str]] = []  # Lista de microservice_id iniciales
    resources: ResourcesDTO  # Recursos asignados al servicio
    policy_id: str  # ID de la política YAML

    def to_model(self, service_id: Optional[str] = None) -> ServiceModel:
        """
        Convierte un DTO de creación en un ServiceModel listo para persistir.
        """
        return ServiceModel(
            service_id=service_id or str(uuid.uuid4()),
            security_policy=self.security_policy.to_model() ,
            microservices=self.microservices or [],
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
            service_id=model.service_id,
            security_policy=SecurityPolicyDTO.from_model(model.security_policy),
            microservices=model.microservices,
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
    microservices: List[str]
    resources: ResourcesDTO
    security_policy: SecurityPolicyResponseDTO

    @staticmethod
    def from_model(model: ServiceModel) -> "ServiceResponseDTO":
        """
        Convierte un ServiceModel en un DTO de respuesta segura.
        """
        return ServiceResponseDTO(
            service_id=model.service_id,
            microservices=model.microservices,
            resources=ResourcesDTO.from_model(model.resources),
            security_policy=SecurityPolicyResponseDTO.from_model(model.security_policy),
        )


# -------------------------------
# DTO para actualización de servicios
# -------------------------------
class ServiceUpdateDTO(BaseModel):
    """
    DTO para actualizar parcialmente un servicio.
    Solo los campos enviados se aplicarán sobre el modelo existente.
    """
    resources: Optional[ResourcesUpdateDTO] = None
    microservices: Optional[List[str]] = None
    security_policy: Optional[SecurityPolicyDTO] = None

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
            elif field == "security_policy" and value is not None:
                security_policy_dto = SecurityPolicyDTO(**value)
                model.security_policy = SecurityPolicyUpdateDTO.apply_updates(security_policy_dto, model.security_policy)
            else:
                setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: ServiceModel) -> "ServiceUpdateDTO":
        """
        Convierte un ServiceModel en un DTO de actualización.
        """
        return ServiceUpdateDTO(
            resources=ResourcesUpdateDTO.from_model(model.resources),
            microservices=model.microservices,
            security_policy=SecurityPolicyUpdateDTO.from_model(model.security_policy)
        )
