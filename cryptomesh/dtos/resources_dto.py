from typing import Optional
from pydantic import BaseModel, field_validator
from cryptomesh.models import ResourcesModel

class ResourcesDTO(BaseModel):
    cpu: int
    ram: str

    @field_validator("cpu")
    def cpu_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("CPU must be greater than 0")
        return v

    @field_validator("ram")
    def ram_format(cls, v):
        v_lower = v.lower()
        if not (v_lower.endswith("gb") or v_lower.endswith("mb")):
            raise ValueError("RAM must be specified in GB or MB, e.g., '4GB' or '512MB'")
        return v

    def to_model(self) -> ResourcesModel:
        """Convierte este DTO en un ResourcesModel."""
        return ResourcesModel(cpu=self.cpu, ram=self.ram)

    @staticmethod
    def from_model(model: ResourcesModel) -> "ResourcesDTO":
        """Convierte un ResourcesModel en un DTO."""
        return ResourcesDTO(cpu=model.cpu, ram=model.ram)


class ResourcesUpdateDTO(BaseModel):
    cpu: Optional[int] = None
    ram: Optional[str] = None

    @field_validator("cpu")
    def cpu_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("CPU must be greater than 0")
        return v

    @field_validator("ram")
    def ram_format(cls, v):
        if v is not None:
            v_lower = v.lower()
            if not (v_lower.endswith("gb") or v_lower.endswith("mb")):
                raise ValueError("RAM must be specified in GB or MB, e.g., '4GB' or '512MB'")
        return v


    @staticmethod
    def apply_updates(dto: "ResourcesUpdateDTO", model: ResourcesModel) -> ResourcesModel:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model

