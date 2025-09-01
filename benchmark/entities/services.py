# benchmark/entities/services.py
import asyncio
from cryptomesh.dtos.services_dto import ServiceCreateDTO, ServiceUpdateDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO, ResourcesUpdateDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES
from typing import List

def build_service(security_policy_id= str) -> ServiceCreateDTO:
    return ServiceCreateDTO(
        security_policy=SecurityPolicyDTO(
            sp_id=security_policy_id,
            roles=["admin"],
            requires_authentication=True
        ),
        microservices=[],  # opcional, se pueden agregar después
        resources=ResourcesDTO(cpu=2, ram="1GB"),
        policy_id="policy_benchmark"
    )

async def bench_services(client, logger, security_policy_ids: List[str]) -> List [str]:
    created_ids = []

    # ------------------ CREATE en batches ------------------
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [
            build_service(security_policy_ids[j % len(security_policy_ids)]) for j in range(BATCH_SIZE)
        ]
        results = await limited_gather([
            log_operation(logger, "POST.SERVICE", "/api/v1/services/", client.create_service(dto))
            for dto in batch
        ], max_concurrent=MAX_CONCURRENT)

        for r in results:
            if r and r.is_ok:
                created_ids.append(r.unwrap().service_id)
            else:
                print("⚠️ Error, POST no devolvió service_id:", r)

        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)


    # ------------------ GET en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "GET.SERVICE", f"/api/v1/services/{sid}/", client.get_service(sid))
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ UPDATE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "PUT.SERVICE",
                f"/api/v1/services/{sid}/",
                client.update_service(sid, ServiceUpdateDTO(resources=ResourcesUpdateDTO(cpu=4, ram="2GB")))
            )
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ DELETE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "DELETE.SERVICE", f"/api/v1/services/{sid}/", client.delete_service(sid))
            for sid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids