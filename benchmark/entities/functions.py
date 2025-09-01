# benchmark/entities/functions.py
import asyncio
from typing import List
from cryptomesh.dtos.functions_dto import FunctionCreateDTO, FunctionUpdateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from cryptomesh.dtos.storage_dto import StorageDTO, StorageUpdateDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES

def build_function(microservice_id: str, endpoint_id: str) -> FunctionCreateDTO:
    """
    Construye un DTO de función para benchmark.
    """
    return FunctionCreateDTO(
        microservice_id=microservice_id,
        endpoint_id=endpoint_id,
        image="my_function_image:latest",
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        storage=StorageDTO(capacity="1GB", source_path="/data/source", sink_path="/data/sink"),
        policy_id="policy_benchmark"
    )

async def bench_functions(client, logger, microservice_ids: List[str], endpoint_ids: List[str]):
    created_ids = []

    # ------------------ CREATE en batches ------------------
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [build_function(microservice_ids[j % len(microservice_ids)], endpoint_ids[j % len(endpoint_ids)]) for j in range(BATCH_SIZE)]
        results = await limited_gather([
            log_operation(logger, "POST.FUNCTION", "/api/v1/functions/", client.create_function(dto))
            for dto in batch
        ], max_concurrent=MAX_CONCURRENT)

        for r in results:
            if r and r.is_ok:
                created_ids.append(r.unwrap().function_id)
            else:
                print("⚠️ Error, POST no devolvió function_id:", r)

        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)


    # ------------------ GET en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "GET.FUNCTION", f"/api/v1/functions/{fid}", client.get_function(fid))
            for fid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ UPDATE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "PUT.FUNCTION",
                f"/api/v1/functions/{fid}",
                client.update_function(fid, FunctionUpdateDTO(resources=ResourcesUpdateDTO(cpu=2, ram="1GB")))
            )
            for fid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ DELETE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "DELETE.FUNCTION", f"/api/v1/functions/{fid}", client.delete_function(fid))
            for fid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids