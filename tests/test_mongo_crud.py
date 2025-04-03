import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from cryptomesh.repositories.services import ServicesRepository
from cryptomesh.models import ServiceModel, SecurityPolicy

@pytest.mark.asyncio
async def test_insert_service():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.cryptomesh_test
    repo = ServicesRepository(collection=db.services)

    service = ServiceModel(
        security_policy=SecurityPolicy(roles=["test_role"], requires_authentication=True),
        microservices={}
    )
    result = await repo.create(service)
    
    assert result.security_policy.roles == ["test_role"]
    await db.services.delete_many({})
