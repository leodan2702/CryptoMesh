from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from cryptomesh.models import FunctionModel
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from cryptomesh.dtos.storage_dto import StorageDTO, StorageUpdateDTO
import uuid

# -------------------------------
# DTO para creación de funciones
# -------------------------------
class FunctionCreateDTO(BaseModel):
    name : str
    microservice_id: str
    image: str
    resources: ResourcesDTO
    storage: StorageDTO
    endpoint_id: str
    policy_id: Optional[str] = None

    def to_model(self, function_id: Optional[str] = None, deployment_status: str = "pending") -> FunctionModel:
        """
        Convierte un FunctionCreateDTO en un FunctionModel listo para persistir.
        """
        return FunctionModel(
            function_id=function_id or str(uuid.uuid4()),
            name=self.name,
            microservice_id=self.microservice_id,
            image=self.image,
            resources=self.resources.to_model(),
            storage=self.storage.to_model(),
            endpoint_id=self.endpoint_id,
            deployment_status=deployment_status,
            created_at=datetime.utcnow(),
            policy_id=self.policy_id
        )

    @staticmethod
    def from_model(model: FunctionModel) -> "FunctionCreateDTO":
        """
        Convierte un FunctionModel a un DTO de creación.
        """
        return FunctionCreateDTO(
            name=model.name,
            microservice_id=model.microservice_id,
            image=model.image,
            resources=ResourcesDTO.from_model(model.resources),
            storage=StorageDTO.from_model(model.storage),
            endpoint_id=model.endpoint_id,
            policy_id=model.policy_id
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class FunctionResponseDTO(BaseModel):
    function_id: str
    name: str
    image: str
    deployment_status: str
    resources: ResourcesDTO
    storage: StorageDTO
    microservice_id: str
    endpoint_id: str

    @staticmethod
    def from_model(model: FunctionModel) -> "FunctionResponseDTO":
        """
        Convierte un FunctionModel en un DTO de respuesta segura.
        """
        return FunctionResponseDTO(
            function_id=model.function_id,
            name=model.name,
            image=model.image,
            deployment_status=model.deployment_status,
            resources=ResourcesDTO.from_model(model.resources),
            storage=StorageDTO.from_model(model.storage),
            microservice_id = model.microservice_id,
            endpoint_id = model.endpoint_id 
        )


# -------------------------------
# DTO para actualización de funciones
# -------------------------------
class FunctionUpdateDTO(BaseModel):
    name: Optional[str] = None
    image: Optional[str] = None
    resources: Optional[ResourcesUpdateDTO] = None
    storage: Optional[StorageUpdateDTO] = None
    endpoint_id: Optional[str] = None
    microservice_id: Optional[str] = None
    deployment_status: Optional[str] = None

    @staticmethod
    def apply_updates(dto: "FunctionUpdateDTO", model: FunctionModel) -> FunctionModel:
        """
        Aplica los cambios del DTO sobre un FunctionModel existente.
        Convierte los DTOs incrustados a modelos internos antes de asignar.
        """
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == "resources" and value is not None:
                resource_dto = ResourcesUpdateDTO(**value)
                model.resources = ResourcesUpdateDTO.apply_updates(resource_dto, model.resources)
            elif field == "storage" and value is not None:
                storage_dto = StorageUpdateDTO(**value)
                model.storage = StorageUpdateDTO.apply_updates(storage_dto, model.storage)
            else:
                setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: FunctionModel) -> "FunctionUpdateDTO":
        """
        Convierte un FunctionModel en un DTO de actualización.
        """
        return FunctionUpdateDTO(
            name=model.name,
            image=model.image,
            resources=ResourcesUpdateDTO.from_model(model.resources),
            storage=StorageUpdateDTO.from_model(model.storage),
            endpoint_id=model.endpoint_id,
            microservice_id=model.microservice_id,
            deployment_status=model.deployment_status
        )
