from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from cryptomesh.models import ResourcesModel
import os

# Límites máximos configurables desde variables de entorno
MAX_CPU = int(os.environ.get("CRYPTOMESH_MAX_CPU", "4"))   # Por defecto 4
MAX_RAM = int(os.environ.get("CRYPTOMESH_MAX_RAM", "8"))   # Por defecto 8GB

class ResourcesDTO(BaseModel):
    cpu: int
    ram: str

    @field_validator("cpu")
    def cpu_must_be_positive(cls, v):
        if v is not None and not (1 <= v <= MAX_CPU):
            raise HTTPException(status_code=400, detail=f"CPU must be between 1 and {MAX_CPU}")
        return v

    @field_validator("ram")
    def ram_format(cls, v):
        if " " in v:
            raise HTTPException(status_code=400, detail="RAM must not contain spaces, e.g., '4GB'")
        if not v.endswith("GB"):
            raise HTTPException(status_code=400, detail="RAM must be specified in GB, e.g., '4GB'")
        try:
            num = int(v.replace("GB", ""))
        except ValueError:
            raise HTTPException(status_code=400, detail="RAM must be a number followed by GB, e.g., '4GB'")
        if not (1 <= num <= MAX_RAM):
            raise HTTPException(status_code=400, detail=f"RAM must be between 1GB and {MAX_RAM}GB")
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
        if v is not None and not (1 <= v <= MAX_CPU):
            raise HTTPException(status_code=400, detail=f"CPU must be between 1 and {MAX_CPU}")
        return v

    @field_validator("ram")
    def ram_format(cls, v):
        if v is not None:
            if " " in v:
                raise HTTPException(status_code=400, detail="RAM must not contain spaces, e.g., '4GB'")
            if not v.endswith("GB"):
                raise HTTPException(status_code=400, detail="RAM must be specified in GB, e.g., '4GB'")
            try:
                num = int(v.replace("GB", ""))
            except ValueError:
                raise HTTPException(status_code=400, detail="RAM must be a number followed by GB, e.g., '4GB'")
            if not (1 <= num <= MAX_RAM):
                raise HTTPException(status_code=400, detail=f"RAM must be between 1GB and {MAX_RAM}GB")
        return v

    @staticmethod
    def apply_updates(dto: "ResourcesUpdateDTO", model: ResourcesModel) -> ResourcesModel:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model
