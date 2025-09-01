# benchmark/entities/function_result.py
import uuid
import asyncio
from typing import List
from cryptomesh.dtos.function_result_dto import FunctionResultCreateDTO, FunctionResultUpdateDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES


def build_function_result(function_id: str) -> FunctionResultCreateDTO:
    """
    Construye un DTO de creación para FunctionResult con datos únicos.
    """
    unique_id = str(uuid.uuid4())
    return FunctionResultCreateDTO(
        function_id=function_id,
        metadata={"trace_id": unique_id, "info": "benchmark result"}
    )


async def bench_function_results(client, logger, function_ids: List[str]):
    created_ids: List[str] = []

    # ------------------ CREATE en batches ------------------
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [
            build_function_result(function_ids[j % len(function_ids)])
            for j in range(BATCH_SIZE)
        ]
        results = await limited_gather([
            log_operation(logger, "POST.FUNCTIONRESULT", "/api/v1/function-results/", client.create_function_result(dto))
            for dto in batch
        ], max_concurrent=MAX_CONCURRENT)

        for r in results:
            if r and r.is_ok:
                created_ids.append(r.unwrap().result_id)
            else:
                print("⚠️ Error, POST no devolvió result_id:", r)

        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ GET en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i + BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "GET.FUNCTIONRESULT", f"/api/v1/function-results/{rid}", client.get_function_result(rid))
            for rid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ UPDATE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i + BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "PUT.FUNCTIONRESULT",
                f"/api/v1/function-results/{rid}",
                client.update_function_result(
                    rid,
                    FunctionResultUpdateDTO(status="completed", output=f"Updated output {rid}")
                )
            )
            for rid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ DELETE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i + BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "DELETE.FUNCTIONRESULT", f"/api/v1/function-results/{rid}", client.delete_function_result(rid))
            for rid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids

