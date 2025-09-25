from pydantic import BaseModel
from typing import List, Optional

# -------------------------------
# DTO para métodos de un ActiveObject
# -------------------------------
class MethodHierarchyDTO(BaseModel):
    name: str  # nombre del método
    parameters: List[str] = []  # nombres de los parámetros

# -------------------------------
# DTO para ActiveObject en la jerarquía
# -------------------------------
class ActiveObjectHierarchyDTO(BaseModel):
    active_object_id: str
    object_name: str
    methods: List[MethodHierarchyDTO] = []

# -------------------------------
# DTO para Microservice en la jerarquía
# -------------------------------
class MicroserviceHierarchyDTO(BaseModel):
    microservice_id: str
    microservice_name: str
    active_objects: List[ActiveObjectHierarchyDTO] = []

# -------------------------------
# DTO para Service en la jerarquía
# -------------------------------
class ServiceHierarchyDTO(BaseModel):
    service_id: str
    service_name: str
    microservices: List[MicroserviceHierarchyDTO] = []
