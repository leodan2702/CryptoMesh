from typing import Optional,Annotated
from fastapi import HTTPException
from pydantic import BaseModel, field_validator,AfterValidator
from cryptomesh.models import ResourcesModel
import os

# Límites máximos configurables desde variables de entorno
MIN_CPU = int(os.environ.get("CRYPTOMESH_MIN_CPU", "1"))   # Por defecto 1
MAX_CPU = int(os.environ.get("CRYPTOMESH_MAX_CPU", "4"))   # Por defecto 4

MIN_RAM = int(os.environ.get("CRYPTOMESH_MIN_RAM", "1"))   # Por defecto 1GB
MAX_RAM = int(os.environ.get("CRYPTOMESH_MAX_RAM", "8"))   # Por defecto 8GB

def is_valid_cpu(v:Optional[int])->Optional[int]:
    if v is not None and not (MIN_CPU <= v <= MAX_CPU):
        raise HTTPException(status_code=400, detail=f"CPU must be between {MIN_CPU} and {MAX_CPU}")
    return v

def is_valid_ram(v:Optional[str])->Optional[str]:
    if " " in v:
        raise HTTPException(status_code=400, detail="RAM must not contain spaces, e.g., '4GB'")
    if not v.endswith("GB"):
        raise HTTPException(status_code=400, detail="RAM must be specified in GB, e.g., '4GB'")
    try:
        num = int(v.replace("GB", ""))
    except ValueError:
        raise HTTPException(status_code=400, detail="RAM must be a number followed by GB, e.g., '4GB'")
    if not (MIN_RAM <= num <= MAX_RAM):
        raise HTTPException(status_code=400, detail=f"RAM must be between {MIN_RAM}GB and {MAX_RAM}GB")
    return v

CPU = Annotated[int,AfterValidator(is_valid_cpu)]
RAM = Annotated[str,AfterValidator(is_valid_ram)]



class ResourcesDTO(BaseModel):
    cpu: CPU
    ram: RAM
    # _validate_cpu = field_validator("cpu", mode="before")(is_valid_cpu)
    # _validate_ram = field_validator("ram", mode="before")(ram_format)

    def to_model(self) -> ResourcesModel:
        """Convierte este DTO en un ResourcesModel."""
        return ResourcesModel(cpu=self.cpu, ram=self.ram)

    @staticmethod
    def from_model(model: ResourcesModel) -> "ResourcesDTO":
        """Convierte un ResourcesModel en un DTO."""
        return ResourcesDTO(cpu=model.cpu, ram=model.ram)


class ResourcesUpdateDTO(BaseModel):
    cpu: CPU
    ram: RAM

    @staticmethod
    def apply_updates(dto: "ResourcesUpdateDTO", model: ResourcesModel) -> ResourcesModel:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model
