# benchmark/utils.py
import asyncio
import time
import json
import os

# -----------------------------
# Logger con queue asíncrona
# -----------------------------
def create_logger(name, path):
    """
    Crea un logger asíncrono que escribe en un archivo JSON línea por línea.
    
    Args:
        name (str): Nombre del worker/log.
        path (str): Ruta del archivo de log.
    
    Returns:
        logger (async function): Función para loguear entradas.
        logger_writer (async function): Tarea que consume la cola y escribe en archivo.
        queue (asyncio.Queue): Cola interna para enviar logs.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    queue = asyncio.Queue()

    async def logger_writer():
        with open(path, "a") as f:
            while True:
                entry = await queue.get()
                if entry is None:  # Señal de cierre
                    break
                # Agregar nombre de logger a cada entrada
                entry['logger_name'] = name
                f.write(json.dumps(entry) + "\n")
                queue.task_done()

    async def logger(entry):
        await queue.put(entry)

    return logger, logger_writer, queue

# -----------------------------
# Función de logging de operaciones
# -----------------------------
async def log_operation(logger, event, path, coro):
    t1 = time.perf_counter()
    result = None
    status = None
    error_msg = None

    try:
        raw_result = await coro  # puede ser Result, HTTP-like o DTO

        if hasattr(raw_result, "is_ok"):  # option.result.Result
            result = raw_result
            status = 200 if raw_result.is_ok else getattr(raw_result.unwrap_err(), "status_code", 500)

        elif hasattr(raw_result, "status_code"):  # HTTP-like
            result = raw_result
            status = raw_result.status_code

        else:
            result = raw_result
            status = 520
            error_msg = f"Unexpected result type: {type(raw_result)}"

    except Exception as e:
        result = None
        status = 500
        error_msg = str(e)

    log_entry = {
        "event": event,
        "path": path,
        "status": status,
        "elapsed": round(time.perf_counter() - t1, 3)
    }

    if error_msg:
        log_entry["error"] = error_msg

    await logger(log_entry)
    return result  # devuelve Result o DTO


# -----------------------------
# Función para limitar concurrencia
# -----------------------------
async def limited_gather(coros, max_concurrent=50):
    """
    Ejecuta corutinas limitando la concurrencia mediante semáforo.
    
    Args:
        coros (list[coroutine]): Lista de corutinas a ejecutar.
        max_concurrent (int): Máximo de corutinas concurrentes.
    
    Returns:
        list: Resultados de las corutinas.
    """
    semaphore = asyncio.Semaphore(max_concurrent)

    async def sem_task(c):
        async with semaphore:
            return await c

    return await asyncio.gather(*(sem_task(c) for c in coros))

