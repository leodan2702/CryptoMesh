from fastapi import FastAPI
import cryptomesh.controllers as Controllers
import uvicorn
from contextlib import asynccontextmanager
from cryptomesh.db import connect_to_mongo,close_mongo_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield 
    await close_mongo_connection()
app = FastAPI(title="CryptoMesh API",lifespan=lifespan)

# Include API routes from the service controller under /api/v1

app.include_router(Controllers.services_router, prefix="/api/v1",tags=["Services"])
app.include_router(Controllers.microservices_router, prefix="/api/v1", tags=["Microservices"])
app.include_router(Controllers.functions_router, prefix="/api/v1", tags=["Functions"])
app.include_router(Controllers.endpoint_router, prefix="/api/v1", tags=["Endpoints"])
app.include_router(Controllers.storage_router, prefix="/api/v1", tags=["Storage"])
app.include_router(Controllers.service_policy_router, prefix="/api/v1", tags=["Service Policy"])
app.include_router(Controllers.roles_router, prefix="/api/v1", tags=["Roles"])
app.include_router(Controllers.endpoint_state_router, prefix="/api/v1", tags=["Endpoint State"])
app.include_router(Controllers.function_state_router, prefix="/api/v1", tags=["Function State"])
app.include_router(Controllers.function_result_router, prefix="/api/v1", tags=["Function Result"])

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=19000)
