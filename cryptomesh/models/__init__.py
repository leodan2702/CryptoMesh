from pydantic import BaseModel

class ServiceModel(BaseModel):
    id:str

class MicroserviceModel(BaseModel):
    pass

class FunctionModel(BaseModel):
    pass