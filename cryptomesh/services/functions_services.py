import time as T
from cryptomesh.models import FunctionModel
from cryptomesh.repositories.functions_repository import FunctionsRepository
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import NotFoundError, ValidationError, CryptoMeshError

L = get_logger(__name__)

class FunctionsService:
    """
    Servicio encargado de gestionar las funciones en la base de datos.
    """

    def __init__(self, repository: FunctionsRepository):
        self.repository = repository

    async def create_function(self, data: FunctionModel):
        t1 = T.time()
        if await self.repository.get_by_id(data.function_id):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "FUNCTION.CREATE.FAIL",
                "reason": "Already exists",
                "function_id": data.function_id,
                "time": elapsed
            })
            raise ValidationError(f"Function '{data.function_id}' already exists")

        function = await self.repository.create(data)
        elapsed = round(T.time() - t1, 4)

        if not function:
            L.error({
                "event": "FUNCTION.CREATE.FAIL",
                "reason": "Failed to create",
                "function_id": data.function_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create function '{data.function_id}'")

        L.info({
            "event": "FUNCTION.CREATED",
            "function_id": data.function_id,
            "time": elapsed
        })
        return function

    async def list_functions(self):
        t1 = T.time()
        functions = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)
        L.debug({
            "event": "FUNCTION.LISTED",
            "count": len(functions),
            "time": elapsed
        })
        return functions

    async def get_function(self, function_id: str):
        t1 = T.time()
        function = await self.repository.get_by_id(function_id)
        elapsed = round(T.time() - t1, 4)

        if not function:
            L.warning({
                "event": "FUNCTION.GET.NOT_FOUND",
                "function_id": function_id,
                "time": elapsed
            })
            raise NotFoundError(function_id)

        L.info({
            "event": "FUNCTION.FETCHED",
            "function_id": function_id,
            "time": elapsed
        })
        return function

    async def update_function(self, function_id: str, updates: dict):
        t1 = T.time()
        if not await self.repository.get_by_id(function_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "FUNCTION.UPDATE.NOT_FOUND",
                "function_id": function_id,
                "time": elapsed
            })
            raise NotFoundError(function_id)

        updated = await self.repository.update(function_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "FUNCTION.UPDATE.FAIL",
                "function_id": function_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update function '{function_id}'")

        L.info({
            "event": "FUNCTION.UPDATED",
            "function_id": function_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_function(self, function_id: str):
        t1 = T.time()
        if not await self.repository.get_by_id(function_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "FUNCTION.DELETE.NOT_FOUND",
                "function_id": function_id,
                "time": elapsed
            })
            raise NotFoundError(function_id)

        success = await self.repository.delete(function_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "FUNCTION.DELETE.FAIL",
                "function_id": function_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to delete function '{function_id}'")

        L.info({
            "event": "FUNCTION.DELETED",
            "function_id": function_id,
            "time": elapsed
        })
        return {"detail": f"Function '{function_id}' deleted"}


