from pydantic import BaseModel, Field, field_validator
from cryptomesh.models import StorageModel
from typing import Optional

class StorageDTO(BaseModel):
    """
    DTO centralizado para almacenamiento.
    Se usa en funciones y microservicios.
    """
    capacity: str
    source_path: str
    sink_path: str

    # -------------------------------
    # Validaciones
    # -------------------------------
    @field_validator("capacity")
    def capacity_format(cls, v):
        v_lower = v.lower()
        if not (v_lower.endswith("gb") or v_lower.endswith("mb")):
            raise ValueError("Capacity must be specified in GB or MB, e.g., '10GB' or '512MB'")
        return v

    @field_validator("source_path", "sink_path")
    def paths_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("Paths cannot be empty")
        return v

    # -------------------------------
    # Métodos de conversión
    # -------------------------------
    def to_model(self) -> StorageModel:
        """
        Convierte un StorageDTO a StorageModel listo para persistir.
        """
        return StorageModel(
            capacity=self.capacity,
            source_path=self.source_path,
            sink_path=self.sink_path
        )

    @staticmethod
    def from_model(model: StorageModel) -> "StorageDTO":
        """
        Convierte un StorageModel a StorageDTO para uso en la capa de transporte.
        """
        return StorageDTO(
            capacity=model.capacity,
            source_path=model.source_path,
            sink_path=model.sink_path
        )


class StorageUpdateDTO(BaseModel):
    capacity: Optional[str] = None
    source_path: Optional[str] = None
    sink_path: Optional[str] = None

    @field_validator("capacity")
    def capacity_format(cls, v):
        if v is not None and not (v.lower().endswith("gb") or v.lower().endswith("mb")):
            raise ValueError("Capacity must be specified in GB or MB, e.g., '10GB'")
        return v

    @field_validator("source_path", "sink_path")
    def paths_must_not_be_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Paths cannot be empty")
        return v

    @staticmethod
    def apply_updates(dto: "StorageUpdateDTO", model: StorageModel) -> StorageModel:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model

