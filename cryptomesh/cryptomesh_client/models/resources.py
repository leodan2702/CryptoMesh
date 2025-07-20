# cryptomesh_client/models/resources.py

from pydantic import BaseModel

class ResourcesModel(BaseModel):
    cpu: int
    ram: str