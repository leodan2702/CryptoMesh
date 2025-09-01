import uuid
import asyncio
from typing import List
from cryptomesh.dtos.endpoint_state_dto import EndpointStateCreateDTO, EndpointStateUpdateDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES


def build_endpoint_state(endpoint_id: str) -> EndpointStateCreateDTO:
    """
    Construye un DTO de creación para EndpointState con datos únicos.
    """
    unique_id = str(uuid.uuid4())
    return EndpointStateCreateDTO(
        endpoint_id=endpoint_id,
        state="initial",
        metadata={"trace_id": unique_id, "info": "benchmark endpoint state"}
    )


async def bench_endpoint_states(client, logger, endpoint_ids: List[str]):
    created_ids: List[str] = []

    # ------------------ CREATE en batches ------------------
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [
            build_endpoint_state(endpoint_ids[j % len(endpoint_ids)])
            for j in range(BATCH_SIZE)
        ]
        results = await limited_gather([
            log_operation(
                logger,
                "POST.ENDPOINTSTATE",
                "/api/v1/endpoint-states/",
                client.create_endpoint_state(dto)
            )
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
            log_operation(
                logger,
                "GET.ENDPOINTSTATE",
                f"/api/v1/endpoint-states/{sid}",
                client.get_endpoint_state(sid)
            )
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ UPDATE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i + BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "PUT.ENDPOINTSTATE",
                f"/api/v1/endpoint-states/{sid}",
                client.update_endpoint_state(
                    sid,
                    EndpointStateUpdateDTO(
                        state="updated",
                        metadata={"updated": "true"}
                    )
                )
            )
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ DELETE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i + BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "DELETE.ENDPOINTSTATE",
                f"/api/v1/endpoint-states/{sid}",
                client.delete_endpoint_state(sid)
            )
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids
