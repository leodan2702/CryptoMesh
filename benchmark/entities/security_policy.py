# benchmark/entities/security_policy.py
import uuid
import asyncio
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO, SecurityPolicyUpdateDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES, SECURITY_POLICY_ID
from typing import List

def build_policy(security_policy_id: str | None = None, roles: List[str] | None = None) -> SecurityPolicyDTO:
    unique_id = str(uuid.uuid4())
    role_ids = ["admin"]
    return SecurityPolicyDTO(
        sp_id=str(security_policy_id or f"{SECURITY_POLICY_ID}_{unique_id}"),  
        name=f"benchmark_policy_{unique_id}",  
        roles=role_ids,
        requires_authentication=True
    )

async def bench_security_policy(client, logger, role_ids: List[str]) :
    created_ids = []

    # ------------------ CREATE en batches ------------------
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [
            build_policy(security_policy_id=None, roles=role_ids)  # pasamos los roles
            for _ in range(BATCH_SIZE)
        ]
        results = await limited_gather([
            log_operation(
                logger,
                "POST.SECURITY_POLICY",
                "/api/v1/security_policies/",
                client.create_security_policy(dto)
            )
            for dto in batch
        ], max_concurrent=MAX_CONCURRENT)

        for r in results:
            if r and r.is_ok:
                created_ids.append(r.unwrap().sp_id)
            else:
                print("⚠️ Error, POST no devolvió sp_id:", r)

        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)


    # ------------------ GET en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "GET.SECURITY_POLICY", f"/api/v1/security_policies/{sp_id}/", client.get_security_policy(sp_id))
            for sp_id in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ UPDATE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "PUT.SECURITY_POLICY",
                f"/api/v1/security_policies/{sp_id}/",
                client.update_security_policy(sp_id, SecurityPolicyUpdateDTO(name=f"Updated Policy {sp_id}"))
            )
            for sp_id in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ DELETE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "DELETE.SECURITY_POLICY", f"/api/v1/security_policies/{sp_id}/", client.delete_security_policy(sp_id))
            for sp_id in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids