from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from cryptomesh.models import EndpointModel
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
import uuid
from typing import Optional

class DeleteEndpointDTO(BaseModel):
    detail: str
# -------------------------------
# DTO para creación de endpoints
# -------------------------------
class EndpointCreateDTO(BaseModel):
    """
    DTO para recibir datos de creación de un endpoint.
    Incluye nombre, imagen del contenedor, recursos y política de seguridad.
    """
    name: str
    image: str
    resources: ResourcesDTO
    security_policy: str
    policy_id: Optional[str] = None  # referencia a la política YAML

    def to_model(self, endpoint_id: Optional[str] = None) -> EndpointModel:
        """
        Convierte un DTO de creación en un EndpointModel listo para persistir.
        """
        return EndpointModel(
            endpoint_id=endpoint_id or str(uuid.uuid4()),
            name=self.name,
            image=self.image,
            resources= self.resources.to_model(),
            security_policy= self.security_policy,
            created_at=datetime.utcnow(),
            policy_id=self.policy_id
        )

    @staticmethod
    def from_model(model: EndpointModel) -> "EndpointCreateDTO":
        """
        Convierte un EndpointModel a un DTO de creación.
        """
        return EndpointCreateDTO(
            name=model.name,
            image=model.image,
            resources=ResourcesDTO.from_model(model.resources),
            security_policy=model.security_policy,
            policy_id=model.policy_id
        )
    
    

# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class EndpointResponseDTO(BaseModel):
    """
    DTO que se envía al cliente al consultar endpoints.
    Contiene solo información segura y relevante.
    """
    endpoint_id: str
    name: str
    image: str
    resources: ResourcesDTO
    security_policy: str

    @staticmethod
    def from_model(model: EndpointModel) -> "EndpointResponseDTO":
        """
        Convierte un EndpointModel en un DTO de respuesta segura.
        """
        return EndpointResponseDTO(
            endpoint_id=model.endpoint_id,
            name=model.name,
            image=model.image,
            resources=ResourcesDTO.from_model(model.resources),
            security_policy=model.security_policy
        )


# -------------------------------
# DTO para actualización de endpoints
# -------------------------------
class EndpointUpdateDTO(BaseModel):
    """
    DTO para actualizar parcialmente un endpoint.
    Solo los campos enviados se aplicarán sobre el modelo existente.
    """
    name: Optional[str] = None
    image: Optional[str] = None
    resources: Optional[ResourcesUpdateDTO] = None
    security_policy: Optional[str] = None

    @staticmethod
    def apply_updates(dto: "EndpointUpdateDTO", model: EndpointModel) -> EndpointModel:
        """
        Aplica los cambios del DTO sobre un EndpointModel existente.
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
    def from_model(model: EndpointModel) -> "EndpointUpdateDTO":
        """
        Convierte un EndpointModel en un DTO de actualización,
        usando los valores actuales del modelo para prellenar formularios o interfaces.
        """
        return EndpointUpdateDTO(
            name=model.name,
            image=model.image,
            resources=ResourcesUpdateDTO.from_model(model.resources),
            security_policy= model.security_policy
        )
