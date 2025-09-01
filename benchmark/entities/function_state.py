# benchmark/entities/function_state.py
import uuid
import asyncio
from typing import List
from cryptomesh.dtos.function_state_dto import FunctionStateCreateDTO, FunctionStateUpdateDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES


def build_function_state(function_id: str) -> FunctionStateCreateDTO:
    """
    Construye un DTO de creación para FunctionState con datos únicos.
    """
    unique_id = str(uuid.uuid4())
    return FunctionStateCreateDTO(
        function_id=function_id,
        state="initialized",
        metadata={"trace_id": unique_id, "info": "benchmark state"}
    )


async def bench_function_states(client, logger, function_ids: List[str]):
    created_ids: List[str] = []

    # ------------------ CREATE en batches ------------------
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [
            build_function_state(function_ids[j % len(function_ids)])
            for j in range(BATCH_SIZE)
        ]
        results = await limited_gather([
            log_operation(logger, "POST.FUNCTIONSTATE", "/api/v1/function-states/", client.create_function_state(dto))
            for dto in batch
        ], max_concurrent=MAX_CONCURRENT)

        for r in results:
            if r and r.is_ok:
                created_ids.append(r.unwrap().state_id)
            else:
                print("⚠️ Error, POST no devolvió state_id:", r)

        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ GET en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i + BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "GET.FUNCTIONSTATE", f"/api/v1/function-states/{sid}", client.get_function_state(sid))
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ UPDATE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i + BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "PUT.FUNCTIONSTATE",
                f"/api/v1/function-states/{sid}",
                client.update_function_state(
                    sid,
                    FunctionStateUpdateDTO(state="completed", metadata={"updated": "yes","sid": str(sid)})
                )
            )
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ DELETE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i + BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "DELETE.FUNCTIONSTATE", f"/api/v1/function-states/{sid}", client.delete_function_state(sid))
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids
