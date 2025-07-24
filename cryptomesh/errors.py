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
