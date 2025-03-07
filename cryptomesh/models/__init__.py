from typing import List
from pydantic import BaseModel

    
class SecurityPolicy(BaseModel):
    """
    SecurityPolicy defines the security roles required for accessing or managing a service.

    Attributes
    ----------
    roles : List[str]
        A list of role names that are allowed to interact with the service.
    """
    roles: List[str]


class MicroserviceModel(BaseModel):
    """
    MicroserviceModel represents a microservice within a larger service.

    This model is intended to be extended with additional attributes that describe
    the microservice configuration, such as its name, resources, or specific functions.
    """
    pass


class ServiceModel(BaseModel):
    """
    ServiceModel encapsulates the details of a service in the CryptoMesh architecture.

    Attributes
    ----------
    id : str
        A unique identifier for the service.
    security_policy : SecurityPolicy
        The security policy that governs access to the service.
    microservices : List[MicroserviceModel]
        A list of microservices that belong to this service.
    """
    id: str
    security_policy: SecurityPolicy
    microservices: List[MicroserviceModel]


class FunctionModel(BaseModel):
    """
    FunctionModel represents an individual function within a microservice.

    This model should be extended with attributes that define the function's behavior,
    such as the container image, resources, storage requirements, etc.
    """
    pass


class Policy(BaseModel):
    """
    Policy defines the overall configuration for the CryptoMesh system.

    It encapsulates the top-level identifier for the CryptoMesh configuration and a list of services.

    Attributes
    ----------
    cryptomesh : str
        A top-level identifier or version string for the CryptoMesh configuration.
    services : List[ServiceModel]
        A list of services that are defined in the CryptoMesh configuration.
    """
    cryptomesh: str
    services: List[ServiceModel]





