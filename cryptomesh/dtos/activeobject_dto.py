from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import uuid
from cryptomesh.models import ActiveObjectModel, FunctionModel


# -------------------------------
# DTO para creación de ActiveObject
# -------------------------------
class ActiveObjectCreateDTO(BaseModel):
    """
    DTO para recibir datos de creación de un ActiveObject.
    """
    axo_is_read_only: Optional[bool] = False
    axo_key: Optional[str] = None
    axo_bucket_id: Optional[str] = None
    axo_source_bucket_id: Optional[str] = None
    axo_sink_bucket_id: Optional[str] = None
    axo_module: str
    axo_class_name: str
    axo_version: int = 0
    axo_endpoint_id: Optional[str] = None
    axo_microservice_id: str
    axo_dependencies: Optional[List[str]] = []
    axo_uri: Optional[str] = None
    axo_alias: Optional[str] = None
    path: Optional[str] = "/axo/data"
    source_path: Optional[str] = "/axo/source"
    sink_path: Optional[str] = "/axo/sink"
    axo_code: Optional[str] = None

    def to_model(self, active_object_id: Optional[str] = None) -> ActiveObjectModel:
        """
        Convierte un DTO de creación en un ActiveObjectModel listo para persistir.
        """
        return ActiveObjectModel(
            active_object_id=active_object_id or str(uuid.uuid4()),
            axo_is_read_only=self.axo_is_read_only,
            axo_key=self.axo_key or str(uuid.uuid4()),
            axo_bucket_id=self.axo_bucket_id or str(uuid.uuid4()),
            axo_source_bucket_id=self.axo_source_bucket_id or str(uuid.uuid4()),
            axo_sink_bucket_id=self.axo_sink_bucket_id or str(uuid.uuid4()),
            axo_module=self.axo_module,
            axo_class_name=self.axo_class_name,
            axo_version=self.axo_version,
            axo_endpoint_id=self.axo_endpoint_id,
            axo_microservice_id=self.axo_microservice_id,
            axo_dependencies=self.axo_dependencies or [],
            axo_uri=self.axo_uri,
            axo_alias=self.axo_alias,
            path=self.path,
            source_path=self.source_path,
            sink_path=self.sink_path,
            axo_code=self.axo_code
        )

    @staticmethod
    def from_model(model: ActiveObjectModel) -> "ActiveObjectCreateDTO":
        """
        Convierte un ActiveObjectModel a un DTO de creación.
        """
        return ActiveObjectCreateDTO(
            axo_is_read_only=model.axo_is_read_only,
            axo_key=model.axo_key,
            axo_bucket_id=model.axo_bucket_id,
            axo_source_bucket_id=model.axo_source_bucket_id,
            axo_sink_bucket_id=model.axo_sink_bucket_id,
            axo_module=model.axo_module,
            axo_class_name=model.axo_class_name,
            axo_version=model.axo_version,
            axo_endpoint_id=model.axo_endpoint_id,
            axo_microservice_id=model.axo_microservice_id,
            axo_dependencies=model.axo_dependencies,
            axo_uri=model.axo_uri,
            axo_alias=model.axo_alias,
            path=model.path,
            source_path=model.source_path,
            sink_path=model.sink_path,
            axo_code=model.axo_code
        )


# -------------------------------
# DTO para respuesta al cliente
# -------------------------------
class ActiveObjectResponseDTO(BaseModel):
    """
    DTO que se envía al cliente al consultar ActiveObjects.
    Incluye los campos relevantes para el frontend o API cliente.
    """
    active_object_id: str
    axo_is_read_only: bool
    axo_key: str
    axo_bucket_id: str
    axo_source_bucket_id: str
    axo_sink_bucket_id: str
    axo_module: str
    axo_class_name: str
    axo_version: int
    axo_endpoint_id: Optional[str]
    axo_microservice_id: str
    axo_dependencies: List[str]
    axo_uri: Optional[str]
    axo_alias: Optional[str]
    path: str
    source_path: str
    sink_path: str
    axo_code: Optional[str]
    axo_schema: Optional[Dict[str, object]] = None
    functions: List[FunctionModel] = []

    @staticmethod
    def from_model(model: ActiveObjectModel) -> "ActiveObjectResponseDTO":
        return ActiveObjectResponseDTO(
            active_object_id=model.active_object_id,
            axo_is_read_only=model.axo_is_read_only,
            axo_key=model.axo_key,
            axo_bucket_id=model.axo_bucket_id,
            axo_source_bucket_id=model.axo_source_bucket_id,
            axo_sink_bucket_id=model.axo_sink_bucket_id,
            axo_module=model.axo_module,
            axo_class_name=model.axo_class_name,
            axo_version=model.axo_version,
            axo_endpoint_id=model.axo_endpoint_id,
            axo_microservice_id=model.axo_microservice_id,
            axo_dependencies=model.axo_dependencies,
            axo_uri=model.axo_uri,
            axo_alias=model.axo_alias,
            path=model.path,
            source_path=model.source_path,
            sink_path=model.sink_path,
            axo_code=model.axo_code,
            axo_schema=model.axo_schema,
            functions=[
                f if isinstance(f, FunctionModel) else FunctionModel(**f)
                for f in (model.functions or [])
            ]
        )


# -------------------------------
# DTO para actualización de ActiveObject
# -------------------------------
class ActiveObjectUpdateDTO(BaseModel):
    """
    DTO para actualizar parcialmente un ActiveObject.
    Solo los campos enviados se aplicarán sobre el modelo existente.
    """
    axo_is_read_only: Optional[bool] = None
    axo_key: Optional[str] = None
    axo_bucket_id: Optional[str] = None
    axo_source_bucket_id: Optional[str] = None
    axo_sink_bucket_id: Optional[str] = None
    axo_module: Optional[str] = None
    axo_class_name: Optional[str] = None
    axo_version: Optional[int] = None
    axo_endpoint_id: Optional[str] = None
    axo_microservice_id: Optional[str] = None
    axo_dependencies: Optional[List[str]] = None
    axo_uri: Optional[str] = None
    axo_alias: Optional[str] = None
    path: Optional[str] = None
    source_path: Optional[str] = None
    sink_path: Optional[str] = None

    @staticmethod
    def apply_updates(dto: "ActiveObjectUpdateDTO", model: ActiveObjectModel) -> ActiveObjectModel:
        """
        Aplica los cambios del DTO sobre un ActiveObjectModel existente.
        """
        update_data = dto.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(model, field, value)
        return model

    @staticmethod
    def from_model(model: ActiveObjectModel) -> "ActiveObjectUpdateDTO":
        return ActiveObjectUpdateDTO(
            axo_is_read_only=model.axo_is_read_only,
            axo_key=model.axo_key,
            axo_bucket_id=model.axo_bucket_id,
            axo_source_bucket_id=model.axo_source_bucket_id,
            axo_sink_bucket_id=model.axo_sink_bucket_id,
            axo_module=model.axo_module,
            axo_class_name=model.axo_class_name,
            axo_version=model.axo_version,
            axo_endpoint_id=model.axo_endpoint_id,
            axo_microservice_id=model.axo_microservice_id,
            axo_dependencies=model.axo_dependencies,
            axo_uri=model.axo_uri,
            axo_alias=model.axo_alias,
            path=model.path,
            source_path=model.source_path,
            sink_path=model.sink_path,
            axo_code=model.axo_code
        )
