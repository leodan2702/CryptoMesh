class CryptoMeshError(Exception):
    def __init__(self, message: str, code: str = "internal_error"):
        self.message = message
        self.code = code
        super().__init__(f"[{code}] {message}")

    def to_dict(self):
        return {
            "message": self.message,
            "code": self.code
        }

class FunctionNotFound(CryptoMeshError):
    def __init__(self, fn_id: str):
        super().__init__(f"Function '{fn_id}' was not found", code="function_not_found")

class InvalidYAML(CryptoMeshError):
    def __init__(self, detail: str):
        super().__init__(f"Invalid YAML format: {detail}", code="invalid_yaml")


class ValidationError(CryptoMeshError):
    def __init__(self, detail: str):
        super().__init__(f"Validation error: {detail}", code="validation_error")


class UnauthorizedError(CryptoMeshError):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(detail, code="unauthorized")

class NotFoundError(CryptoMeshError):
    def __init__(self, resource: str):
        super().__init__(f"Resource '{resource}' not found", code="not_found")


class CreationError(CryptoMeshError):
    def __init__(self, entity_type: str, entity_id: str, original_exception: Exception):
        message = f"Error creating {entity_type} '{entity_id}': {str(original_exception)}"
        super().__init__(message=message, code="creation_error")
