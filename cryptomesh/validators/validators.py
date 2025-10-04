from typing import Annotated, Callable
from pydantic import AfterValidator

# Definir un valor máximo global
MAX_LEN = 32

def max_length_validator(max_len: int, field_label: str) -> Callable[[str], str]:
    """Crea un validador que revisa que la longitud de una cadena no exceda `max_len`."""
    def validator_name(value: str) -> str:
        if len(value) > max_len:
            raise ValueError(f"{field_label} cannot exceed {max_len} characters.")
        return value
    return validator_name

# Tipos anotados reutilizables con MAX_LEN
ServiceNameStr = Annotated[str, AfterValidator(max_length_validator(MAX_LEN, "Service name"))]
MicroserviceNameStr = Annotated[str, AfterValidator(max_length_validator(MAX_LEN, "Microservice name"))]
RoleNameStr = Annotated[str, AfterValidator(max_length_validator(MAX_LEN, "Role name"))]
EndpointNameStr = Annotated[str, AfterValidator(max_length_validator(MAX_LEN, "Endpoint name"))]
SecurityPolicyNameStr = Annotated[str, AfterValidator(max_length_validator(MAX_LEN, "Security Policy name"))]
paramNameStr = Annotated[str, AfterValidator(max_length_validator(MAX_LEN, "Parameter name"))]
FunctionNameStr = Annotated[str, AfterValidator(max_length_validator(MAX_LEN, "Function name"))]
AxoNameStr = Annotated[str, AfterValidator(max_length_validator(MAX_LEN, "Axo alias"))]


