# benchmark/entities/roles.py
import uuid
import asyncio
from typing import List
from cryptomesh.dtos.role_dto import RoleCreateDTO, RoleUpdateDTO
from benchmark.utils import log_operation, limited_gather
from benchmark.config import ITERATIONS, MAX_CONCURRENT, BATCH_SIZE, PAUSE_BETWEEN_BATCHES

def build_role() -> RoleCreateDTO:
    """
    Construye un DTO de Role para benchmark.
    """
    return RoleCreateDTO(
        name=f"role",
        description=f"Role for benchmarking",
        permissions=["read", "write", "delete"]
    )

async def bench_roles(client, logger):
    created_ids: List[str] = []

    # ------------------ CREATE en batches ------------------
    for i in range(0, ITERATIONS, BATCH_SIZE):
        batch = [build_role() for _ in range(BATCH_SIZE)]
        results = await limited_gather([
            log_operation(logger, "POST.ROLE", "/api/v1/roles/", client.create_role(dto))
            for dto in batch
        ], max_concurrent=MAX_CONCURRENT)

        for r in results:
            if r and r.is_ok:
                created_ids.append(r.unwrap().role_id)
            else:
                print("⚠️ Error, POST no devolvió role_id:", r)

        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)


    # ------------------ GET en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "GET.ROLE", f"/api/v1/roles/{role_id}", client.get_role(role_id))
            for role_id in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ UPDATE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(
                logger,
                "PUT.ROLE",
                f"/api/v1/roles/{role_id}",
                client.update_role(role_id, RoleUpdateDTO(description=f"Updated role {role_id}"))
            )
            for role_id in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    # ------------------ DELETE en batches ------------------
    for i in range(0, len(created_ids), BATCH_SIZE):
        batch_ids = created_ids[i:i+BATCH_SIZE]
        await limited_gather([
            log_operation(logger, "DELETE.ROLE", f"/api/v1/roles/{role_id}", client.delete_role(role_id))
            for role_id in batch_ids
        ], max_concurrent=MAX_CONCURRENT)
        await asyncio.sleep(PAUSE_BETWEEN_BATCHES)

    return created_ids