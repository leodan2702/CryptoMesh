# benchmark/entities/endpoints.py
import asyncio
from cryptomesh.dtos.endpoints_dto import EndpointCreateDTO, EndpointUpdateDTO
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO
from cryptomesh.dtos.resources_dto import ResourcesDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES
from typing import List

def build_endpoint(security_policy_id= str):
    return EndpointCreateDTO(
        name="ep_bench",
        image="axo:endpoint",
        resources=ResourcesDTO(cpu=1, ram="512MB"),
        security_policy=SecurityPolicyDTO(
            sp_id=security_policy_id,
            roles=["admin"],
            requires_authentication=True
        ),
        policy_id="policy_benchmark"
    )

async def bench_endpoints(client, logger, security_policy_ids: List[str]) -> List [str]:
    created_ids = []
    # POST en batches
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [
            build_endpoint(security_policy_ids[j % len(security_policy_ids)])
            for j in range(BATCH_SIZE)
        ]
        results = await limited_gather([
            log_operation(logger, "POST.ENDPOINT", "/api/v1/endpoints/", client.create_endpoint(dto))
            for dto in batch
        ], max_concurrent=MAX_CONCURRENT)

        for r in results:
            if r.is_ok:
                created_ids.append(r.unwrap().endpoint_id)
            else:
                print("post fallo,", r.unwrap_err())

        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # GET en batches
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "GET.ENDPOINT", f"/api/v1/endpoints/{eid}/", client.get_endpoint(eid))
            for eid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # UPDATE en batches
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "PUT.ENDPOINT", f"/api/v1/endpoints/{eid}/",
                          client.update_endpoint(eid, EndpointUpdateDTO(name="endpoint_updated")))
            for eid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # DELETE en batches
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "DELETE.ENDPOINT", f"/api/v1/endpoints/{eid}/", client.delete_endpoint(eid))
            for eid in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids