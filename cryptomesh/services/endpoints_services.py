import time as T
from typing import Optional,List,Dict,Any
from option import Result,Ok,Err,Some
import random
# 
import humanfriendly as HF
from cryptomesh.models import EndpointModel,SummonerParams
from cryptomesh.dtos.endpoints_dto import DeleteEndpointDTO
from cryptomesh.repositories.endpoints_repository import EndpointsRepository
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError,
)
from mictlanx.services.summoner.summoner import Summoner,SummonContainerPayload,SummonServiceResponse,ExposedPort,MountX,MountType

L = get_logger(__name__)

class EndpointsService:
    """
    Servicio encargado de gestionar los endpoints y sus relaciones con las políticas de seguridad.
    """

    def __init__(self, 
        repository: EndpointsRepository, 
        security_policy_service: SecurityPolicyService,
        summoner_params:Optional[SummonerParams] = SummonerParams()
    ):
        self.repository = repository
        self.security_policy_service = security_policy_service
        self.summoner_params = summoner_params
        self.summoner = Summoner(
            ip_addr     = summoner_params.ip_addr,
            port        = summoner_params.port,
            protocol    = summoner_params.protocol,
            api_version = Some(summoner_params.api_version)
        )
    async def get_count(self,filter:Dict[str,Any]={})->Result[int,Exception]:
        try:
            x = await self.repository.collection.count_documents(filter=filter)
            return Ok(x)
        except Exception as e:
            L.error({
                "error_code":600,
                "detail":"Failed to get endpoint count",
                "error":str(e)
            })
            return Err(e)
    
    async def detach(self,endpoint_id:str)->Result[bool,CryptoMeshError]:
        try:
            res1 = self.summoner.delete_container(container_id=endpoint_id,mode=self.summoner_params.mode)
            res2 = await self.delete_endpoint(endpoint_id=endpoint_id)
            return Ok(res1.is_ok and res2.is_ok)
        except Exception as e:
            return CryptoMeshError(message=str(e),code=500)
    async def deploy(self,endpoint_id:str,dependencies:List[str]=[],network_id:str = "axo-net",selected_node:str= None):
        model = await self.get_endpoint(endpoint_id=endpoint_id)
        x_port = random.randrange(start=30000, stop=60000)
        envs = {
            # --- AXO core ---
            "AXO_ENDPOINT_ID": model.envs.get("AXO_ENDPOINT_ID", "axo-endpoint-0"),
            "AXO_GOSSIP_BIND_HOST": model.envs.get("AXO_GOSSIP_BIND_HOST", "0.0.0.0"),
            "AXO_GOSSIP_PORT": model.envs.get("AXO_GOSSIP_PORT", "7777"),
            "AXO_HEARTBEAT_INTERVAL": model.envs.get("AXO_HEARTBEAT_INTERVAL", "5.0"),
            "AXO_GOSSIP_SEEDS": model.envs.get("AXO_GOSSIP_SEEDS", ""),  # space-separated
            "AXO_HEARTBEAT_TTL": model.envs.get("AXO_HEARTBEAT_TTL", "30"),

            "AXO_LOGGER_PATH": model.envs.get("AXO_LOGGER_PATH", "/log"),
            "AXO_LOGGER_WHEN": model.envs.get("AXO_LOGGER_WHEN", "h"),
            "AXO_LOGGER_INTERVAL": model.envs.get("AXO_LOGGER_INTERVAL", "24"),
            "AXO_SYNC_MAX_IDLE_TIME": model.envs.get("AXO_SYNC_MAX_IDLE_TIME", "24h"),
            "AXO_HEATER_TICK_TIME": model.envs.get("AXO_HEATER_TICK_TIME", "30s"),
            "AXO_DEBUG": model.envs.get("AXO_DEBUG", "1"),

            "AXO_SINK_PATH": model.envs.get("AXO_SINK_PATH", "/axo"),
            "AXO_SOURCE_PATH": model.envs.get("AXO_SOURCE_PATH", "/axo/source"),
            "AXO_DATA_PATH": model.envs.get("AXO_DATA_PATH", "/data"),
            "AXO_ENDPOINT_IMAGE": model.envs.get("AXO_ENDPOINT_IMAGE", "nachocode/axo:endpoint-0.0.3a0"),
            "AXO_ENDPOINT_DEPENDENCIES": model.envs.get("AXO_ENDPOINT_DEPENDENCIES", ""),  # semicolon-separated
            "AXO_PROTOCOL": model.envs.get("AXO_PROTOCOL", "tcp"),
            "AXO_PUB_SUB_PORT": model.envs.get("AXO_PUB_SUB_PORT", "16666"),
            "AXO_REQ_RES_PORT": model.envs.get("AXO_REQ_RES_PORT", "16667"),
            "AXO_HOSTNAME": model.envs.get("AXO_HOSTNAME", "127.0.0.1"),
            "AXO_SUBSCRIBER_HOSTNAME": model.envs.get("AXO_SUBSCRIBER_HOSTNAME", "*"),
            "AXO_ENDPOINTS": model.envs.get("AXO_ENDPOINTS", ""),  # space-separated
            "AXO_HEATER_MAX_IDLE_TIME": model.envs.get("AXO_HEATER_MAX_IDLE_TIME", "1h"),
            "AXO_METADATA_TIMEOUT": model.envs.get("AXO_METADATA_TIMEOUT", "30"),
            "AXO_METRICS_COLLECTOR_DEFAULT_LIMIT": model.envs.get("AXO_METRICS_COLLECTOR_DEFAULT_LIMIT", "-1"),
            "AXO_NETWORK_ID": model.envs.get("AXO_NETWORK_ID", "mictlanx"),

            # --- MictlanX Summoner ---
            "MICTLANX_SUMMONER_IP_ADDR": model.envs.get("MICTLANX_SUMMONER_IP_ADDR", "localhost"),
            "MICTLANX_SUMMONER_API_VERSION": model.envs.get("MICTLANX_SUMMONER_API_VERSION", "3"),
            "MICTLANX_SUMMONER_NETWORK": model.envs.get("MICTLANX_SUMMONER_NETWORK", "10.0.0.0/25"),
            "MICTLANX_SUMMONER_PORT": model.envs.get("MICTLANX_SUMMONER_PORT", "15000"),
            "MICTLANX_SUMMONER_PROTOCOL": model.envs.get("MICTLANX_SUMMONER_PROTOCOL", "http"),
            "MICTLANX_SUMMONER_MODE": model.envs.get("MICTLANX_SUMMONER_MODE", "docker"),

            # --- MictlanX client / bucket / routers ---
            "MICTLANX_BUCKET_ID": model.envs.get("MICTLANX_BUCKET_ID", "activex"),
            "MICTLANX_ROUTERS": model.envs.get("MICTLANX_ROUTERS", "mictlanx-router-0:localhost:60666"),
            "MICTLANX_CLIENT_ID": model.envs.get("MICTLANX_CLIENT_ID", "activex-mictlanx-0"),
            "MICTLANX_DEBUG": model.envs.get("MICTLANX_DEBUG", "0"),
            "MICTLANX_LOG_INTERVAL": model.envs.get("MICTLANX_LOG_INTERVAL", "24"),
            "MICTLANX_LOG_WHEN": model.envs.get("MICTLANX_LOG_WHEN", "h"),
            "MICTLANX_LOG_OUTPUT_PATH": model.envs.get("MICTLANX_LOG_OUTPUT_PATH", "/log"),
            "MICTLANX_MAX_WORKERS": model.envs.get("MICTLANX_MAX_WORKERS", "4"),

            # --- Aliases (explicit defaults) ---
            "NODE_IP_ADDR": model.envs.get("NODE_IP_ADDR", "axo-endpoint-0"),  # mirrors AXO_ENDPOINT_ID default
            "NODE_PORT": model.envs.get("NODE_PORT", "16667"),                 # mirrors AXO_REQ_RES_PORT default
        }

        print("PORT",x_port)
        payload = SummonContainerPayload(
            container_id  = model.endpoint_id,
            cpu_count     = model.resources.cpu,
            envs          = envs,
            exposed_ports = [
                ExposedPort(host_port=x_port,container_port=x_port,ip_addr=None, protocolo=None),
                ExposedPort(host_port=x_port+1,container_port=x_port+1,ip_addr=None, protocolo=None),
            ],
            force         = True,
            hostname      = model.endpoint_id,
            image         = model.image,
            ip_addr       = model.endpoint_id,
            labels        = {"crypytomesh":"1", "type":"axo-endpoint"},
            memory        = HF.parse_size(model.resources.ram),
            mounts        = [
                MountX(
                    source     = f"{endpoint_id}-log",
                    target     = "/log",
                    mount_type = MountType.VOLUME,
                ),
                MountX(
                    source     = f"{endpoint_id}-data",
                    target     = "/data",
                    mount_type = MountType.VOLUME,
                ),
            ],
            network_id    = network_id,
            selected_node = selected_node,
            shm_size      = None,
        )
        return self.summoner.summon(payload=payload)

    async def create_endpoint(self, data: EndpointModel):
        t1 = T.time()
        # pasar id_field para que get_by_id busque por "endpoint_id"
        if await self.repository.get_by_id(data.endpoint_id, id_field="endpoint_id"):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "ENDPOINT.CREATE.FAIL",
                "reason": "Already exists",
                "endpoint_id": data.endpoint_id,
                "time": elapsed
            })
            raise ValidationError(f"Endpoint '{data.endpoint_id}' already exists")

        endpoint = await self.repository.create(data)
        elapsed = round(T.time() - t1, 4)

        if not endpoint:
            L.error({
                "event": "ENDPOINT.CREATE.FAIL",
                "reason": "Failed to create",
                "endpoint_id": data.endpoint_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to create endpoint '{data.endpoint_id}'")

        L.info({
            "event": "ENDPOINT.CREATED",
            "endpoint_id": endpoint.endpoint_id,
            "time": elapsed
        })
        return endpoint

    async def list_endpoints(self):
        t1 = T.time()
        endpoints = await self.repository.get_all()
        elapsed = round(T.time() - t1, 4)

        L.debug({
            "event": "ENDPOINT.LISTED",
            "count": len(endpoints),
            "time": elapsed
        })
        return endpoints

    async def get_endpoint(self, endpoint_id: str)->EndpointModel:
        t1 = T.time()
        endpoint = await self.repository.get_by_id(endpoint_id, id_field="endpoint_id")
        elapsed = round(T.time() - t1, 4)

        if not endpoint:
            L.warning({
                "event": "ENDPOINT.GET.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise NotFoundError(endpoint_id)

        L.info({
            "event": "ENDPOINT.FETCHED",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        
        return endpoint        

    async def update_endpoint(self, endpoint_id: str, updates: dict): 
        t1 = T.time()
        if not await self.repository.get_by_id(endpoint_id, id_field="endpoint_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ENDPOINT.UPDATE.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise NotFoundError(endpoint_id)

        updated = await self.repository.update({"endpoint_id": endpoint_id}, updates)
        elapsed = round(T.time() - t1, 4)

        if not updated:
            L.error({
                "event": "ENDPOINT.UPDATE.FAIL",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            raise CryptoMeshError(f"Failed to update endpoint '{endpoint_id}'")

        L.info({
            "event": "ENDPOINT.UPDATED",
            "endpoint_id": endpoint_id,
            "updates": updates,
            "time": elapsed
        })
        return updated

    async def delete_endpoint(self, endpoint_id: str)->Result[DeleteEndpointDTO,CryptoMeshError]:
        t1 = T.time()
        # pasar id_field para buscar por "endpoint_id"
        if not await self.repository.get_by_id(endpoint_id, id_field="endpoint_id"):
            elapsed = round(T.time() - t1, 4)
            L.warning({
                "event": "ENDPOINT.DELETE.NOT_FOUND",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            return Err(NotFoundError(endpoint_id))

        # Cambio: query debe ser dict de acuerdo a base_repository.py
        success = await self.repository.delete({"endpoint_id": endpoint_id})
        elapsed = round(T.time() - t1, 4)

        if not success:
            L.error({
                "event": "ENDPOINT.DELETE.FAIL",
                "endpoint_id": endpoint_id,
                "time": elapsed
            })
            return Err(CryptoMeshError(f"Failed to delete endpoint '{endpoint_id}'"))

        L.info({
            "event": "ENDPOINT.DELETED",
            "endpoint_id": endpoint_id,
            "time": elapsed
        })
        return Ok(DeleteEndpointDTO.model_validate({"detail": f"Endpoint '{endpoint_id}' deleted"}))

