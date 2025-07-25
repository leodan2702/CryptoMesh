from fastapi import FastAPI
import cryptomesh.controllers as Controllers
import uvicorn
from contextlib import asynccontextmanager
from cryptomesh.db import connect_to_mongo,close_mongo_connection
import os
import logging
from cryptomesh.log import Log
import time as T
from cryptomesh.log.logger import get_logger
from cryptomesh import config


L =  get_logger("CryptoMesh-server")

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
app = FastAPI(title=config.CRYPTO_MESH_TITLE,lifespan=lifespan)

# Include API routes from the service controller under /api/v1

app.include_router(Controllers.services_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Services"])
app.include_router(Controllers.microservices_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Microservices"])
app.include_router(Controllers.functions_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Functions"])
app.include_router(Controllers.endpoint_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Endpoints"])
app.include_router(Controllers.service_policy_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Service Policy"])
app.include_router(Controllers.roles_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Roles"])
app.include_router(Controllers.endpoint_state_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Endpoint State"])
app.include_router(Controllers.function_state_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Function State"])
app.include_router(Controllers.function_result_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Function Result"])


if __name__ == "__main__":
    uvicorn.run(app, host=config.CRYPTO_MESH_HOST, port=config.CRYPTO_MESH_PORT)

