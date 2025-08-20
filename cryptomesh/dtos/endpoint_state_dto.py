from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from cryptomesh.models import EndpointStateModel
import uuid

# -------------------------------
# DTO para creación de estado de endpoint
# -------------------------------
class EndpointStateCreateDTO(BaseModel):
    """
    DTO para recibir datos de creación de un estado de endpoint.
    Incluye el ID del endpoint, estado y metadatos opcionales.
    """
    endpoint_id: str
    state: str
    metadata: Optional[Dict[str, str]] = {}

    def to_model(self, state_id: Optional[str] = None) -> EndpointStateModel:
        """
        Convierte un DTO de creación en un EndpointStateModel listo para persistir.
        Se puede pasar un state_id si se desea asignar manualmente.
        """
        return EndpointStateModel(
            state_id=state_id or str(uuid.uuid4()),
            endpoint_id=self.endpoint_id,
            state=self.state,
            metadata=self.metadata or {},
            timestamp=datetime.utcnow()
        )

    @staticmethod
    def from_model(model: EndpointStateModel) -> "EndpointStateCreateDTO":
        """
        Convierte un EndpointStateModel a un DTO de creación.
        Útil para pruebas o serialización bidireccional.
        """
        return EndpointStateCreateDTO(
            endpoint_id=model.endpoint_id,
            state=model.state,
            metadata=model.metadata
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class EndpointStateResponseDTO(BaseModel):
    """
    DTO que se envía al cliente al consultar estados de endpoints.
    Incluye información relevante y segura.
    """
    state_id: str
    endpoint_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime

    @staticmethod
    def from_model(model: EndpointStateModel) -> "EndpointStateResponseDTO":
        """
        Convierte un EndpointStateModel en un DTO de respuesta segura.
        """
        return EndpointStateResponseDTO(
            state_id=model.state_id,
            endpoint_id=model.endpoint_id,
            state=model.state,
            metadata=model.metadata,
            timestamp=model.timestamp
        )


# -------------------------------
# DTO para actualización de estado de endpoint
# -------------------------------
class EndpointStateUpdateDTO(BaseModel):
    """
    DTO para actualizar parcialmente un estado de endpoint.
    Solo los campos enviados se aplicarán sobre el modelo existente.
    """
    state: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

    @staticmethod
    def apply_updates(dto: "EndpointStateUpdateDTO", model: EndpointStateModel) -> EndpointStateModel:
        """
        Aplica los cambios del DTO sobre un EndpointStateModel existente.
        Solo actualiza los campos que el cliente envió.
        """
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: EndpointStateModel) -> "EndpointStateUpdateDTO":
        """
        Convierte un EndpointStateModel en un DTO de actualización,
        usando los valores actuales del modelo.
        """
        return EndpointStateUpdateDTO(
            state=model.state,
            metadata=model.metadata
        )
