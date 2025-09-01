import asyncio
import os
import sys
from datetime import datetime

from cryptomesh.cryptomesh_client.client import CryptoMeshClient
from benchmark.utils import create_logger
from benchmark.config import BASE_URL
from benchmark.entities import endpoints, security_policy, roles, microservices, services, functions, function_result, function_state, endpoint_state

# -----------------------------
# Configuración de worker y logs
# -----------------------------
WORKER_ID = sys.argv[1] if len(sys.argv) > 1 else "1"
LOG_DIR = f"benchmark/logs_bench/bench_worker{WORKER_ID}"
os.makedirs(LOG_DIR, exist_ok=True)

# Lista de entidades
entities = ["endpoints", "security_policy", "roles", "microservices", "services", "functions", "function_result", "function_state", "endpoint_state"]

# -----------------------------
# Función principal
# -----------------------------
async def main():
    client = CryptoMeshClient(BASE_URL)
    loggers = {}

    # Crear logger por entidad y lanzar writer_task dentro del loop
    for entity in entities:
        path = f"{LOG_DIR}/{entity}.log"
        logger, writer, queue = create_logger(name=f"{entity}_worker{WORKER_ID}", path=path)
        writer_task = asyncio.create_task(writer()) 
        loggers[entity] = {"logger": logger, "writer_task": writer_task, "queue": queue}

    # Ejecutar benchmarks en orden de dependencias
    role_ids = await roles.bench_roles(client, loggers["roles"]["logger"])
    security_policy_ids = await security_policy.bench_security_policy(client, loggers["security_policy"]["logger"], role_ids)
    endpoint_ids = await endpoints.bench_endpoints(client, loggers["endpoints"]["logger"], security_policy_ids)
    service_ids = await services.bench_services(client, loggers["services"]["logger"], security_policy_ids)
    microservice_ids = await microservices.bench_microservices(client, loggers["microservices"]["logger"], service_ids)
    function_ids = await functions.bench_functions(client, loggers["functions"]["logger"], microservice_ids, endpoint_ids)
    await function_result.bench_function_results(client, loggers["function_result"]["logger"], function_ids)  
    await function_state.bench_function_states(client, loggers["function_state"]["logger"], function_ids)  
    await endpoint_state.bench_endpoint_states(client, loggers["endpoint_state"]["logger"], endpoint_ids)  



    # Señal para cerrar todos los loggers
    for entity in entities:
        await loggers[entity]["queue"].put(None)

    # Espera a que terminen de escribir todos los logs
    await asyncio.gather(*(loggers[entity]["writer_task"] for entity in entities))

# -----------------------------
# Ejecutar
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
