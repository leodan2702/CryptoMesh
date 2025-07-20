import asyncio
from cryptomesh.cryptomesh_client.client import CryptoMeshClient
from cryptomesh.log.logger import get_logger

logger = get_logger(__name__)

async def main():
    client = CryptoMeshClient(base_url="http://localhost:19000", token="my-secret")

    try:
        await client.interpret("policies/example.yml")
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
