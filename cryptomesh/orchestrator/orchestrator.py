from cryptomesh.log.logger import get_logger
from cryptomesh_client.client import CryptoMeshClient
from cryptomesh.policies import CMPolicyManager
from cryptomesh.errors import InvalidYAML, CreationError 

logger = get_logger(__name__)

async def orchestrate(policy_file: str, client: CryptoMeshClient):
    try:
        manager = CMPolicyManager(policy_file)
        models = manager.as_models()
    except Exception as e:
        logger.error({
            "event": "POLICY.LOAD.FAIL",
            "reason": str(e),
            "policy_file": policy_file
        }, exc_info=True)
        raise InvalidYAML(f"Failed to load policy file: {str(e)}")

    # 1. Endpoints
    for eid, endpoint in models["endpoints"].items():
        try:
            await client.create_endpoint(endpoint)
            logger.info({
                "event": "ENDPOINT.CREATED",
                "endpoint_id": eid,
                "status": "success"
            })
        except Exception as e:
            err = CreationError("endpoint", eid, e)
            logger.error(err.to_dict())
            continue

    # 2. Functions
    for fid, function in models["functions"].items():
        try:
            await client.create_function(function)
            logger.info({
                "event": "FUNCTION.CREATED",
                "function_id": fid,
                "status": "success"
            })
        except Exception as e:
            err = CreationError("function", fid, e)
            logger.error(err.to_dict())
            continue

    # 3. Microservices
    for msid, microservice in models["microservices"].items():
        try:
            await client.create_microservice(microservice)
            logger.info({
                "event": "MICROSERVICE.CREATED",
                "microservice_id": msid,
                "status": "success"
            })
        except Exception as e:
            err = CreationError("microservice", msid, e)
            logger.error(err.to_dict())
            continue

    # 4. Services
    for sid, service in models["services"].items():
        try:
            await client.create_service(service)
            logger.info({
                "event": "SERVICE.CREATED",
                "service_id": sid,
                "status": "success"
            })
        except Exception as e:
            err = CreationError("service", sid, e)
            logger.error(err.to_dict())
            continue
