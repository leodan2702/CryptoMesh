from fastapi import FastAPI
from cryptomesh.controllers import services_router
from cryptomesh.controllers.microservices import router as microservices_router
from cryptomesh.controllers.functions import router as functions_router
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
app.include_router(services_router, prefix="/api/v1")
app.include_router(microservices_router, prefix="/api/v1")
app.include_router(functions_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=19000)
