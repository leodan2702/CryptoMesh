from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, field_validator
from cryptomesh.models import ResourcesModel

class ResourcesDTO(BaseModel):
    cpu: int
    ram: str

    @field_validator("cpu")
    def cpu_must_be_positive(cls, v):
        if v is not None and not (1 <= v <= 4):
            raise HTTPException(status_code=400, detail="CPU must be between 1 and 4")
        return v

    @field_validator("ram")
    def ram_format(cls, v):
        if " " in v:
            raise HTTPException(status_code=400, detail="RAM must not contain spaces, e.g., '4GB'")
        v_lower = v.lower()
        if not v_lower.endswith("gb"):
            raise HTTPException(status_code=400, detail="RAM must be specified in GB, e.g., '4GB'")
        try:
            num = int(v_lower.replace("gb", ""))
        except ValueError:
            raise HTTPException(status_code=400, detail="RAM must be a number followed by GB, e.g., '4GB'")
        if not (1 <= num <= 8):
            raise HTTPException(status_code=400, detail="RAM must be between 1GB and 8GB")
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
        if v is not None and not (1 <= v <= 4):
            raise HTTPException(status_code=400, detail="CPU must be between 1 and 4")
        return v

    @field_validator("ram")
    def ram_format(cls, v):
        if v is not None:
            if " " in v:
                raise HTTPException(status_code=400, detail="RAM must not contain spaces, e.g., '4GB'")
            v_lower = v.lower()
            if not v_lower.endswith("gb"):
                raise HTTPException(status_code=400, detail="RAM must be specified in GB, e.g., '4GB'")
            try:
                num = int(v_lower.replace("gb", ""))
            except ValueError:
                raise HTTPException(status_code=400, detail="RAM must be a number followed by GB, e.g., '4GB'")
            if not (1 <= num <= 8):
                raise HTTPException(status_code=400, detail="RAM must be between 1GB and 8GB")
        return v

    @staticmethod
    def apply_updates(dto: "ResourcesUpdateDTO", model: ResourcesModel) -> ResourcesModel:
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model
