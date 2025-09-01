# benchmark/entities/microservices.py
import asyncio
from typing import List
from cryptomesh.dtos.microservices_dto import MicroserviceCreateDTO, MicroserviceUpdateDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES

def build_microservice(service_id: str) -> MicroserviceCreateDTO:
    return MicroserviceCreateDTO(
        service_id=service_id,
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        functions=[],
        policy_id="policy_benchmark"
    )

async def bench_microservices(client, logger, service_ids: List[str]):
    created_ids = []

    # ------------------ CREATE en batches ------------------
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [build_microservice(service_ids[j % len(service_ids)]) for j in range(BATCH_SIZE)]
        results = await limited_gather([
            log_operation(logger, "POST.MICROSERVICE", "/api/v1/microservices/", client.create_microservice(dto))
            for dto in batch
        ], max_concurrent=MAX_CONCURRENT)

        for r in results:
            if r and r.is_ok:
                created_ids.append(r.unwrap().microservice_id)
            else:
                print("⚠️ Error, POST no devolvió microservice_id:", r)

        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)


    # ------------------ GET en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "GET.MICROSERVICE", f"/api/v1/microservices/{mid}/", client.get_microservice(mid))
            for mid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ UPDATE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "PUT.MICROSERVICE",
                f"/api/v1/microservices/{mid}/",
                client.update_microservice(mid, MicroserviceUpdateDTO(resources=ResourcesUpdateDTO(cpu=2, ram="1GB")))
            )
            for mid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ DELETE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "DELETE.MICROSERVICE", f"/api/v1/microservices/{mid}/", client.delete_microservice(mid))
            for mid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids