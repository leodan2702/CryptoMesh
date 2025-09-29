from cryptomesh.dtos import ActiveObjectCreateDTO
from option import Result,Ok,Err
from uuid import uuid4
from cryptomesh.utils import Utils
from axo.models import MetadataX
from axo.storage import AxoStorage,AxoObjectBlob,AxoObjectBlobs
from cryptomesh.models import ActiveObjectModel
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import CryptoMeshError
import time as T    


L = get_logger(__name__)


class StorageService:
    def __init__(self,axo_storage:AxoStorage):
        self.axo_storage = axo_storage

    async def delete_blobs(self, bucket_id: str, key: str) -> Result[bool, CryptoMeshError]:
        t1 = T.time()

        res = await self.axo_storage.delete_object(
            bucket_id = bucket_id,
            key       = key
        )
        
        return 
      
    async def put_blobs(
        self, 
        dto: ActiveObjectCreateDTO,
    ) -> Result[ActiveObjectModel, CryptoMeshError]:
        t1 = T.time()
        model            = dto.to_model()
        code             = model.axo_code
        axo_bucket_id    = dto.axo_bucket_id or uuid4().hex
        axo_key          = dto.axo_alias
        axo_class_name   = Utils.get_class_name_from_code(code)
        # 
        model.axo_class_name = axo_class_name
        model.axo_bucket_id  = axo_bucket_id
        model.axo_key        = axo_key


        
        
        # For now keep the dict but when we have more time we create a DTO
        # to handle this metadata
        L.debug({
            "event": "API.ACTIVE_OBJECT.CREATING",
            **model.model_dump()
        })
        attrs = {
            "_acx_metadata": MetadataX(
                axo_is_read_only     = False,
                # This is the hack to related the source code with the attrs
                axo_key              = model.axo_alias,
                axo_bucket_id        = axo_bucket_id,
                axo_sink_bucket_id   = model.axo_sink_bucket_id or uuid4().hex,
                axo_source_bucket_id = model.axo_source_bucket_id or uuid4().hex,
                axo_alias            = model.axo_alias,
                axo_class_name       = axo_class_name,
                axo_dependencies     = model.axo_dependencies,
                axo_endpoint_id      = model.axo_endpoint_id,
                axo_module           = model.axo_module or "GenericModule",
                axo_uri              = model.axo_uri,
                axo_version          = model.axo_version,
            ),
            "_acx_local":False,
            "_acx_remote":True
        }
        blobs = AxoObjectBlob.from_code_and_attrs(
            bucket_id = axo_bucket_id,
            key       = axo_key,
            code      = code,
            attrs     = attrs,
        )
        res = await self.axo_storage.put_blobs(
            bucket_id  = axo_bucket_id,
            key        = axo_key,
            blobs      = blobs,
            class_name = model.axo_class_name
        )
        if res.is_err:
            L.error({
                "event": "AXO_BLOB.CREATE.ERROR",
                "reason": res.unwrap_err(),
                **dto.model_dump(),
                "response_time": round(T.time() - t1, 4)
            })
            e = res.unwrap_err()
            return  CryptoMeshError(
                message = e.message,
                code    = e.code
            )
        L.info({
            "event": "AXO_BLOB.CREATED",
            "ok":res.is_ok,
            **dto.model_dump(),
            "response_time": round(T.time() - t1, 4)}
        )
        return Ok(model)