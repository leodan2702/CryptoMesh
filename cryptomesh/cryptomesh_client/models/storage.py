# cryptomesh_client/models/storage.py

from pydantic import BaseModel

class StorageModel(BaseModel):
    capacity: str
    storage_id: str
    source_path: str
    sink_path: str
