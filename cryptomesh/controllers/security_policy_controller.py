from fastapi import APIRouter, Depends, status, Response, HTTPException
from typing import List
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.db import get_collection
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import CryptoMeshError, NotFoundError, ValidationError
from cryptomesh.errors import handle_crypto_errors
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO, SecurityPolicyResponseDTO, SecurityPolicyUpdateDTO
import time as T

router = APIRouter()
L = get_logger(__name__)

def get_security_policy_service() -> SecurityPolicyService:
    collection = get_collection("security_policies")
    repository = SecurityPolicyRepository(collection)
    return SecurityPolicyService(repository)

@router.post(
    "/security-policies/",
    response_model=SecurityPolicyResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una política de seguridad",
    description="Crea una nueva política de seguridad en la base de datos."
)
@handle_crypto_errors
async def create_policy(dto: SecurityPolicyDTO, svc: SecurityPolicyService = Depends(get_security_policy_service)):
    t1 = T.time()
    model = dto.to_model()
    created_policy = await svc.create_policy(model)

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SECURITY_POLICY.CREATED",
        "policy_id": created_policy.sp_id,
        "time": elapsed
    })
    return SecurityPolicyResponseDTO.from_model(created_policy)

@router.get(
    "/security-policies/{sp_id}/",
    response_model=SecurityPolicyResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener una política de seguridad",
    description="Recupera una política de seguridad por su ID."
)
@handle_crypto_errors
async def get_policy(sp_id: str, svc: SecurityPolicyService = Depends(get_security_policy_service)):
    t1 = T.time()
    policy = await svc.get_policy(sp_id)
    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SECURITY_POLICY.FETCHED",
        "policy_id": sp_id,
        "time": elapsed
    })
    return SecurityPolicyResponseDTO.from_model(policy)

@router.get(
    "/security-policies/",
    response_model=List[SecurityPolicyResponseDTO],
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Obtener todas las políticas de seguridad",
    description="Recupera todas las políticas de seguridad almacenadas en la base de datos."
)
@handle_crypto_errors
async def list_policies(svc: SecurityPolicyService = Depends(get_security_policy_service)):
    t1 = T.time()
    policies = await svc.list_policies()
    elapsed = round(T.time() - t1, 4)
    L.debug({
        "event": "API.SECURITY_POLICY.LISTED",
        "count": len(policies),
        "time": elapsed
    })
    return [SecurityPolicyResponseDTO.from_model(p) for p in policies]

@router.put(
    "/security-policies/{sp_id}/",
    response_model=SecurityPolicyResponseDTO,
    response_model_by_alias=True,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una política de seguridad",
    description="Actualiza una política de seguridad existente."
)
@handle_crypto_errors
async def update_policy(sp_id: str, dto:SecurityPolicyUpdateDTO, svc: SecurityPolicyService = Depends(get_security_policy_service)):
    t1 = T.time()
    existing_policy = await svc.get_policy(sp_id)
    updated_model = SecurityPolicyUpdateDTO.apply_updates(dto, existing_policy)
    saved_policy = await svc.update_policy(sp_id, updated_model.model_dump(by_alias=True))

    elapsed = round(T.time() - t1, 4)
    L.info({
        "event": "API.SECURITY_POLICY.UPDATED",
        "policy_id": sp_id,
        "time": elapsed
    })
    return SecurityPolicyResponseDTO.from_model(saved_policy)

@router.delete(
    "/security-policies/{sp_id}/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar una política de seguridad",
    description="Elimina una política de seguridad existente."
)
@handle_crypto_errors
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


