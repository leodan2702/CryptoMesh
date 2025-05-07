import time as T
from fastapi import HTTPException
from typing import List
from cryptomesh.models import FunctionResultModel
from cryptomesh.repositories.function_result_repository import FunctionResultRepository
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class FunctionResultService:
    """
    Servicio encargado de gestionar los resultados de funciones en la base de datos.
    """

    def __init__(self, repository: FunctionResultRepository):
        self.repository = repository

    async def create_result(self, result: FunctionResultModel):
        t1 = T.time()
        if await self.repository.get_by_id(result.state_id):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "FUNCTION_RESULT.CREATE.FAIL",
                "reason": "Already exists",
                "state_id": result.state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=400, detail="Function result already exists")

        created = await self.repository.create(result)
        elapsed = round(T.time() - t1, 4)

        if not created:
            L.error({
                "event": "FUNCTION_RESULT.CREATE.FAIL",
                "reason": "Failed to create",
                "state_id": result.state_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to create function result")

        L.info({
            "event": "FUNCTION_RESULT.CREATED",
            "state_id": result.state_id,
            "time": elapsed
        })
        return created

    async def list_results(self) -> List[FunctionResultModel]:
        t1 = T.time()
        results = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)

        L.debug({
            "event": "FUNCTION_RESULT.LISTED",
            "count": len(results),
            "time": elapsed
        })
        return results

    async def get_result(self, result_id: str) -> FunctionResultModel:
        t1 = T.time()
        result = await self.repository.get_by_id(result_id)
        elapsed = round(T.time() - t1, 4)

        if not result:
            L.warning({
                "event": "FUNCTION_RESULT.GET.NOT_FOUND",
                "result_id": result_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Function result not found")

        L.info({
            "event": "FUNCTION_RESULT.FETCHED",
            "result_id": result_id,
            "time": elapsed
        })
        return result

    async def update_result(self, result_id: str, updates: dict) -> FunctionResultModel:
        t1 = T.time()
        if not await self.repository.get_by_id(result_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "FUNCTION_RESULT.UPDATE.NOT_FOUND",
                "result_id": result_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Function result not found")

        updated = await self.repository.update(result_id, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "FUNCTION_RESULT.UPDATE.FAIL",
                "result_id": result_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to update function result")

        L.info({
            "event": "FUNCTION_RESULT.UPDATED",
            "result_id": result_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_result(self, result_id: str) -> dict:
        t1 = T.time()
        if not await self.repository.get_by_id(result_id):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "FUNCTION_RESULT.DELETE.NOT_FOUND",
                "result_id": result_id,
                "time": elapsed
            })
            raise HTTPException(status_code=404, detail="Function result not found")

        success = await self.repository.delete(result_id)
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "FUNCTION_RESULT.DELETE.FAIL",
                "result_id": result_id,
                "time": elapsed
            })
            raise HTTPException(status_code=500, detail="Failed to delete function result")

        L.info({
            "event": "FUNCTION_RESULT.DELETED",
            "result_id": result_id,
            "time": elapsed
        })
        return {"detail": f"Function result '{result_id}' deleted"}
