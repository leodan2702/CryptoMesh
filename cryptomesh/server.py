from fastapi import FastAPI
import cryptomesh.controllers as Controllers
import uvicorn
from contextlib import asynccontextmanager
from cryptomesh.db import connect_to_mongo,close_mongo_connection
import os
import logging
from cryptomesh.log import Log
import time as T

CRYPTO_MESH_HOST = os.environ.get("CRYPTO_MESH_HOST","0.0.0.0")
CRYPTO_MESH_PORT = int(os.environ.get("CRYPTO_MESH_PORT",19000))
CRYPTO_MESH_DEBUG = bool(int(os.environ.get("CRYPTO_MESH_DEBUG","1")))
CRYPTO_MESH_TITLE = os.environ.get("CRYPTO_MESH_TITLE", "CryptoMesh API")
CRYPTO_MESH_API_PREFIX = os.environ.get("CRYPTO_MESH_API_PREFIX", "/api/v1")
CRYPTO_MESH_LOG_PATH = os.environ.get("CRYPTO_MESH_LOG_PATH", "./logs")

def console_handler_filter(lr:logging.LogRecord):
    if CRYPTO_MESH_DEBUG:
        return CRYPTO_MESH_DEBUG
    
    return lr.levelno == logging.INFO or lr.levelno == logging.ERROR or lr.levelno == logging.WARNING
        

L = Log(
    name=__name__,
    console_handler_filter= console_handler_filter,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    t1 = T.time()
    L.debug({
        "event":"TRY.CONNECTING.DB"
    })
    await connect_to_mongo()
    L.info({
        "event":"DB.CONNECTED",
        "time":T.time() - t1 
    })
    yield 
    await close_mongo_connection()
app = FastAPI(title="CRYPTO_MESH_TITLE",lifespan=lifespan)

# Include API routes from the service controller under /api/v1

app.include_router(Controllers.services_router, prefix=CRYPTO_MESH_API_PREFIX,tags=["Services"])
app.include_router(Controllers.microservices_router, prefix=CRYPTO_MESH_API_PREFIX, tags=["Microservices"])
app.include_router(Controllers.functions_router, prefix=CRYPTO_MESH_API_PREFIX, tags=["Functions"])
app.include_router(Controllers.endpoint_router, prefix=CRYPTO_MESH_API_PREFIX, tags=["Endpoints"])
app.include_router(Controllers.service_policy_router, prefix=CRYPTO_MESH_API_PREFIX, tags=["Service Policy"])
app.include_router(Controllers.roles_router, prefix=CRYPTO_MESH_API_PREFIX, tags=["Roles"])
app.include_router(Controllers.endpoint_state_router, prefix=CRYPTO_MESH_API_PREFIX, tags=["Endpoint State"])
app.include_router(Controllers.function_state_router, prefix=CRYPTO_MESH_API_PREFIX, tags=["Function State"])
app.include_router(Controllers.function_result_router, prefix=CRYPTO_MESH_API_PREFIX, tags=["Function Result"])

if __name__ == "__main__":
    uvicorn.run(app, host=CRYPTO_MESH_HOST,port=CRYPTO_MESH_PORT)
