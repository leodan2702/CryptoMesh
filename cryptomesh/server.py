from fastapi import FastAPI
import cryptomesh.controllers as Controllers
import uvicorn
from contextlib import asynccontextmanager
from cryptomesh.db import connect_to_mongo,close_mongo_connection
import time as T
from cryptomesh.log.logger import get_logger
from cryptomesh import config
from fastapi.middleware.cors import CORSMiddleware
print("Starting CryptoMesh API...")
L =  get_logger("CryptoMesh-server")
@asynccontextmanager
async def lifespan(app: FastAPI):
    t1 = T.time()
    L.debug({
        "event":"TRY.CONNECTING.DB",
        "t1":t1
    })
    await connect_to_mongo()
    L.info({
        "event":"DB.CONNECTED",
        "time":T.time() - t1 
    })
    yield 
    await close_mongo_connection()

app = FastAPI(title=config.CRYPTO_MESH_TITLE,lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","*"],            # exact matches only, use ["*"] to allow all (not recommended in prod)
    allow_credentials=True,           # allows cookies, Authorization headers, etc.
    allow_methods=["*"],              # HTTP methods allowed (GET, POST, etc.)
    allow_headers=["*"],              # HTTP request headers allowed
)
# Include API routes from the service controller under /api/v1
# app.include_router(Controllers.cryptomesh_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Cryptomesh"])

app.include_router(Controllers.services_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Services"])
app.include_router(Controllers.microservices_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Microservices"])
app.include_router(Controllers.functions_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Functions"])
app.include_router(Controllers.endpoint_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Endpoints"])
app.include_router(Controllers.activeobjects_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Active Objects"])
app.include_router(Controllers.hierarchy_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Hierarchy"])
app.include_router(Controllers.service_policy_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Security Policy"])
app.include_router(Controllers.roles_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Roles"])
app.include_router(Controllers.endpoint_state_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Endpoint State"])
app.include_router(Controllers.function_state_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Function State"])
app.include_router(Controllers.function_result_router, prefix=config.CRYPTO_MESH_API_PREFIX, tags=["Function Result"])
if __name__ == "__main__":
    uvicorn.run(app, host=config.CRYPTO_MESH_HOST, port=config.CRYPTO_MESH_PORT)

