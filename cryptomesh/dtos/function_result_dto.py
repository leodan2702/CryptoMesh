from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime
from cryptomesh.models import FunctionResultModel
import uuid

# -------------------------------
# DTO para creación de resultados de función
# -------------------------------
class FunctionResultCreateDTO(BaseModel):
    """
    DTO para registrar un nuevo resultado de una función.
    Incluye el ID de la función y los metadatos asociados al resultado.
    """
    function_id: str
    metadata: Optional[Dict[str, str]] = {}

    def to_model(self, result_id: Optional[str] = None) -> FunctionResultModel:
        return FunctionResultModel(
            result_id=result_id or str(uuid.uuid4()),
            function_id=self.function_id,
            metadata=self.metadata or {},
            timestamp=datetime.utcnow()
        )

    @staticmethod
    def from_model(model: FunctionResultModel) -> "FunctionResultCreateDTO":
        return FunctionResultCreateDTO(
            function_id=model.function_id,
            metadata=model.metadata
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class FunctionResultResponseDTO(BaseModel):
    """
    DTO que se envía al cliente al consultar resultados de funciones.
    Contiene únicamente información segura y relevante.
    """
    result_id: str
    function_id: str
    metadata: Dict[str, str]
    timestamp: datetime

    @staticmethod
    def from_model(model: FunctionResultModel) -> "FunctionResultResponseDTO":
        return FunctionResultResponseDTO(
            result_id=model.result_id,
            function_id=model.function_id,
            metadata=model.metadata,
            timestamp=model.timestamp
        )

class FunctionResultUpdateDTO(BaseModel):
    metadata: Optional[Dict[str, str]] = None

    @staticmethod
    def apply_updates(dto: "FunctionResultUpdateDTO", model: FunctionResultModel) -> FunctionResultModel:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        model.timestamp = datetime.utcnow()  # actualizar timestamp automáticamente
        return model

    @staticmethod
    def from_model(model: FunctionResultModel) -> "FunctionResultUpdateDTO":
        return FunctionResultUpdateDTO(
            metadata=model.metadata
        )