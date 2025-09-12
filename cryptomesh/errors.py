from fastapi import HTTPException
from typing import Any, Callable
from functools import wraps



class CryptoMeshError(Exception):
    def __init__(self, message: str, code: int = 500):
        self.message = message
        self.code = code 
        super().__init__(f"[{code}] {message}")

    def to_dict(self):
        return {
            "message": self.message,
            "code": self.code
        }

    def to_http_exception(self):
        """
        Convert to FastAPI HTTPException
        """
        return HTTPException(status_code=self.code, detail=self.to_dict())

    @staticmethod
    def from_exception(e: Exception)-> "CryptoMeshError":
        """
        Convert a generic exception to a CryptoMeshError
        """
        if isinstance(e, CryptoMeshError):
            return e
        return CryptoMeshError(message=str(e), code=500)


class FunctionNotFound(CryptoMeshError):
    def __init__(self, fn_id: str):
        super().__init__(f"Function '{fn_id}' was not found", code=404)


class InvalidYAML(CryptoMeshError):
    def __init__(self, detail: str):
        super().__init__(f"Invalid YAML format: {detail}", code=400)


class ValidationError(CryptoMeshError):
    def __init__(self, detail: str):
        super().__init__(f"Validation error: {detail}", code=422)


class UnauthorizedError(CryptoMeshError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail, code=401)


class NotFoundError(CryptoMeshError):
    def __init__(self, resource: str):
        super().__init__(f"Resource '{resource}' not found", code=404)


class CreationError(CryptoMeshError):
    def __init__(self, entity_type: str, entity_id: str, original_exception: Exception):
        message = f"Error creating {entity_type} '{entity_id}': {str(original_exception)}"
        super().__init__(message=message, code=500)


# Decorator
def handle_crypto_errors(func: Callable) -> Callable:
    """
    Decorator to handle CryptoMeshError exceptions in FastAPI endpoints
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        try:
            return await func(*args, **kwargs)
        except CryptoMeshError as e:
            raise e.to_http_exception()
        except Exception as e:
            raise CryptoMeshError.from_exception(e).to_http_exception()
    return wrapper
