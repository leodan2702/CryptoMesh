from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from cryptomesh.models import MicroserviceModel
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
import uuid

# -------------------------------
# DTO para creación de microservicios
# -------------------------------
class MicroserviceCreateDTO(BaseModel):
    """
    DTO para recibir datos de creación de un microservicio.
    Incluye el ID del servicio padre, recursos, funciones iniciales y política asociada.
    """
    service_id: str
    resources: ResourcesDTO
    functions: Optional[List[str]] = []  # Lista de funciones asociadas (opcional)
    policy_id: str

    def to_model(self, microservice_id: Optional[str] = None) -> MicroserviceModel:
        """
        Convierte un DTO de creación en un MicroserviceModel listo para persistir.
        """
        return MicroserviceModel(
            microservice_id=microservice_id or str(uuid.uuid4()),
            service_id=self.service_id,
            functions=self.functions or [],
            resources=self.resources.to_model(),
            created_at=datetime.utcnow(),
            policy_id=self.policy_id
        )

    @staticmethod
    def from_model(model: MicroserviceModel) -> "MicroserviceCreateDTO":
        """
        Convierte un MicroserviceModel a un DTO de creación.
        """
        return MicroserviceCreateDTO(
            service_id=model.service_id,
            resources=ResourcesDTO.from_model(model.resources),
            functions=model.functions,
            policy_id=model.policy_id
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class MicroserviceResponseDTO(BaseModel):
    """
    DTO que se envía al cliente al consultar microservicios.
    Solo incluye información segura y relevante.
    """
    microservice_id: str
    service_id: str
    functions: List[str]
    resources: ResourcesDTO

    @staticmethod
    def from_model(model: MicroserviceModel) -> "MicroserviceResponseDTO":
        """
        Convierte un MicroserviceModel a un DTO de respuesta segura.
        """
        return MicroserviceResponseDTO(
            microservice_id=model.microservice_id,
            service_id=model.service_id,
            functions=model.functions,
            resources=ResourcesDTO.from_model(model.resources),
        )


# -------------------------------
# DTO para actualización de microservicios
# -------------------------------
class MicroserviceUpdateDTO(BaseModel):
    """
    DTO para actualizar parcialmente un microservicio.
    Solo los campos enviados se aplicarán sobre el modelo existente.
    """
    resources: Optional[ResourcesUpdateDTO] = None
    functions: Optional[List[str]] = None

    @staticmethod
    def apply_updates(dto: "MicroserviceUpdateDTO", model: MicroserviceModel) -> MicroserviceModel:
        """
        Aplica los cambios del DTO sobre un MicroserviceModel existente.
        Convierte los DTOs incrustados a modelos internos antes de asignar.
        """
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "resources" and value is not None:
                resource_dto = ResourcesUpdateDTO(**value)
                model.resources = ResourcesUpdateDTO.apply_updates(resource_dto, model.resources)
                continue
            setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: MicroserviceModel) -> "MicroserviceUpdateDTO":
        """
        Convierte un MicroserviceModel en un DTO de actualización.
        """
        return MicroserviceUpdateDTO(
            resources=ResourcesUpdateDTO.from_model(model.resources),
            functions=model.functions
        )
