from fastapi import APIRouter, Depends, status, Response
from typing import List
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
import time as T

router = APIRouter()
L = get_logger(__name__)

def get_security_policy_service() -> SecurityPolicyService:
    collection = get_collection("security_policies")
    repository = SecurityPolicyRepository(collection)
    return SecurityPolicyService(repository)

@router.post(
    "/security-policies/",
    response_model=SecurityPolicyModel,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una política de seguridad",
    description="Crea una nueva política de seguridad en la base de datos."
)
async def create_policy(policy: SecurityPolicyModel, svc: SecurityPolicyService = Depends(get_security_policy_service)):
    t1 = T.time()
    result = await svc.create_policy(policy)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SECURITY_POLICY.CREATED",
        "policy_id": policy.sp_id,
        "time": elapsed
    })
    return result

@router.get(
    "/security-policies/{sp_id}",
    response_model=SecurityPolicyModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener una política de seguridad",
    description="Recupera una política de seguridad por su ID."
)
async def get_policy(sp_id: str, svc: SecurityPolicyService = Depends(get_security_policy_service)):
    t1 = T.time()
    policy = await svc.get_policy(sp_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SECURITY_POLICY.FETCHED",
        "policy_id": sp_id,
        "time": elapsed
    })
    return policy

@router.get(
    "/security-policies/",
    response_model=List[SecurityPolicyModel],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todas las políticas de seguridad",
    description="Recupera todas las políticas de seguridad almacenadas en la base de datos."
)
async def list_policies(svc: SecurityPolicyService = Depends(get_security_policy_service)):
    t1 = T.time()
    policies = await svc.list_policies()
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.SECURITY_POLICY.LISTED",
        "count": len(policies),
        "time": elapsed
    })
    return policies

@router.put(
    "/security-policies/{sp_id}",
    response_model=SecurityPolicyModel,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una política de seguridad",
    description="Actualiza una política de seguridad existente."
)
async def update_policy(sp_id: str, updated_policy: SecurityPolicyModel, svc: SecurityPolicyService = Depends(get_security_policy_service)):
    updates = updated_policy.model_dump(by_alias=True, exclude_unset=True)
    t1 = T.time()
    result = await svc.update_policy(sp_id, updates)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SECURITY_POLICY.UPDATED",
        "policy_id": sp_id,
        "updates": updates,
        "time": elapsed
    })
    return result

@router.delete(
    "/security-policies/{sp_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una política de seguridad",
    description="Elimina una política de seguridad existente."
)
async def delete_policy(sp_id: str, svc: SecurityPolicyService = Depends(get_security_policy_service)):
    t1 = T.time()
    await svc.delete_policy(sp_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SECURITY_POLICY.DELETED",
        "policy_id": sp_id,
        "time": elapsed
    })
    return Response(status_code=status.HTTP_204_NO_CONTENT)


