import asyncio
from cryptomesh.orchestrator.orchestrator import orchestrate
from cryptomesh_client.client import CryptoMeshClient
from cryptomesh.log.logger import get_logger

logger = get_logger(__name__)

async def main():
    try:
        client = CryptoMeshClient(base_url="http://localhost:19000", token="my-secret")
        await orchestrate("policies/example.yml", client)
        logger.info({
            "event": "POLICY.INDEX.SUCCESS",
            "status": "All entities indexed successfully"
        })
    except Exception as e:
        logger.error({
            "event": "POLICY.INDEX.FAILURE",
            "error": str(e)
        }, exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
