# cryptomesh/log/logger_config.py

import logging
from cryptomesh.config import (
    CRYPTO_MESH_DEBUG,
    CRYPTO_MESH_LOG_PATH,
    CRYPTO_MESH_LOG_LEVEL,
    CRYPTO_MESH_LOG_ROTATION_WHEN,
    CRYPTO_MESH_LOG_ROTATION_INTERVAL,
    CRYPTO_MESH_LOG_TO_FILE,
    CRYPTO_MESH_LOG_ERROR_FILE,
)
from cryptomesh.log import Log

def console_handler_filter(record: logging.LogRecord):
    if CRYPTO_MESH_DEBUG:
        return True
    return record.levelno in (logging.INFO, logging.WARNING, logging.ERROR)

def get_logger(name: str):
    return Log(
        name=name,
        level=getattr(logging, CRYPTO_MESH_LOG_LEVEL.upper(), logging.DEBUG),
        path=CRYPTO_MESH_LOG_PATH,
        console_handler_filter=console_handler_filter,
        to_file=CRYPTO_MESH_LOG_TO_FILE,
        error_log=CRYPTO_MESH_LOG_ERROR_FILE,
        when=CRYPTO_MESH_LOG_ROTATION_WHEN,
        interval=CRYPTO_MESH_LOG_ROTATION_INTERVAL,
    )

# Logger global opcional
L = get_logger("cryptomesh")

