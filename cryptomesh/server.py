from fastapi import FastAPI
from cryptomesh.controllers.services_controller import router as services_router
from cryptomesh.controllers.microservices_controller import router as microservices_router
from cryptomesh.controllers.functions_controller import router as functions_router
from cryptomesh.controllers.endpoints_controller import router as endpoint_router
from cryptomesh.controllers.storage_controller import router as storage_router
from cryptomesh.controllers.security_policy_controller import router as service_policy_router  # <-- Importa el router de Security Policy
from cryptomesh.controllers.roles_controller import router as roles_router
from cryptomesh.controllers.endpoint_state_controller import router as endpoint_state_router
from cryptomesh.controllers.function_state_controller import router as function_state_router
from cryptomesh.controllers.function_result_controller import router as function_result_router

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

app.include_router(services_router, prefix="/api/v1",tags=["Services"])
app.include_router(microservices_router, prefix="/api/v1", tags=["Microservices"])
app.include_router(functions_router, prefix="/api/v1", tags=["Functions"])
app.include_router(endpoint_router, prefix="/api/v1", tags=["Endpoints"])
app.include_router(storage_router, prefix="/api/v1", tags=["Storage"])
app.include_router(service_policy_router, prefix="/api/v1", tags=["Service Policy"])
app.include_router(roles_router, prefix="/api/v1", tags=["Roles"])
app.include_router(endpoint_state_router, prefix="/api/v1", tags=["Endpoint State"])
app.include_router(function_state_router, prefix="/api/v1", tags=["Function State"])
app.include_router(function_result_router, prefix="/api/v1", tags=["Function Result"])
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=19000)
