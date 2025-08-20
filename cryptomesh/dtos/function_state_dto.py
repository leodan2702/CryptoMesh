from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from cryptomesh.models import FunctionStateModel
import uuid

# -------------------------------
# DTO para creación de estado de función
# -------------------------------
class FunctionStateCreateDTO(BaseModel):
    """
    DTO para registrar un nuevo estado de una función.
    Incluye el ID de la función, el estado actual y metadatos opcionales.
    """
    function_id: str
    state: str
    metadata: Optional[Dict[str, str]] = {}

    @staticmethod
    def to_model(dto: "FunctionStateCreateDTO", state_id: Optional[str] = None) -> FunctionStateModel:
        return FunctionStateModel(
            state_id=state_id or str(uuid.uuid4()),
            function_id=dto.function_id,
            state=dto.state,
            metadata=dto.metadata or {},
            timestamp=datetime.utcnow()
        )

    @staticmethod
    def from_model(model: FunctionStateModel) -> "FunctionStateCreateDTO":
        return FunctionStateCreateDTO(
            function_id=model.function_id,
            state=model.state,
            metadata=model.metadata
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class FunctionStateResponseDTO(BaseModel):
    """
    DTO que se envía al cliente al consultar estados de funciones.
    Contiene información segura y relevante.
    """
    state_id: str
    function_id: str
    state: str
    metadata: Dict[str, str]
    timestamp: datetime

    @staticmethod
    def from_model(model: FunctionStateModel) -> "FunctionStateResponseDTO":
        return FunctionStateResponseDTO(
            state_id=model.state_id,
            function_id=model.function_id,
            state=model.state,
            metadata=model.metadata,
            timestamp=model.timestamp
        )


# -------------------------------
# DTO para actualización de estado de función
# -------------------------------
class FunctionStateUpdateDTO(BaseModel):
    """
    DTO para actualizar parcialmente un estado de función.
    Solo los campos enviados se aplicarán sobre el modelo existente.
    """
    state: Optional[str] = None
    metadata: Optional[Dict[str, str]] = None

    @staticmethod
    def apply_updates(dto: "FunctionStateUpdateDTO", model: FunctionStateModel) -> FunctionStateModel:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: FunctionStateModel) -> "FunctionStateUpdateDTO":
        return FunctionStateUpdateDTO(
            state=model.state,
            metadata=model.metadata
        )
