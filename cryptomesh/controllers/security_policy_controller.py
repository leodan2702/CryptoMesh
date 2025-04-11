from fastapi import APIRouter, Depends
from typing import List
from cryptomesh.models import SecurityPolicyModel
from cryptomesh.services.security_policy_service import SecurityPolicyService
from cryptomesh.repositories.security_policy_repository import SecurityPolicyRepository
from cryptomesh.db import get_collection

router = APIRouter()

def get_security_policy_service() -> SecurityPolicyService:
    collection = get_collection("security_policies")
    repository = SecurityPolicyRepository(collection)
    return SecurityPolicyService(repository)

@router.post(
    "/security-policies/",
    response_model=SecurityPolicyModel,
    summary="Crear una política de seguridad",
    description="Crea una nueva política de seguridad en la base de datos."
)
async def create_policy(policy: SecurityPolicyModel, service: SecurityPolicyService = Depends(get_security_policy_service)):
    return await service.create_policy(policy)

@router.get(
    "/security-policies/{sp_id}",
    response_model=SecurityPolicyModel,
    summary="Obtener una política de seguridad",
    description="Recupera una política de seguridad por su ID."
)
async def get_policy(sp_id: str, service: SecurityPolicyService = Depends(get_security_policy_service)):
    return await service.get_policy(sp_id)

@router.get(
    "/security-policies/",
    response_model=List[SecurityPolicyModel],
    summary="Obtener todas las políticas de seguridad",
    description="Recupera todas las políticas de seguridad almacenadas en la base de datos."
)
async def list_policies(service: SecurityPolicyService = Depends(get_security_policy_service)):
    return await service.list_policies()

@router.put(
    "/security-policies/{sp_id}",
    response_model=SecurityPolicyModel,
    summary="Actualizar una política de seguridad",
    description="Actualiza una política de seguridad existente."
)
async def update_policy(
    sp_id: str,
    updated_policy: SecurityPolicyModel,
    service: SecurityPolicyService = Depends(get_security_policy_service)
):
    updates = updated_policy.dict(by_alias=True, exclude_unset=True)
    return await service.update_policy(sp_id, updates)

@router.delete(
    "/security-policies/{sp_id}",
    summary="Eliminar una política de seguridad",
    description="Elimina una política de seguridad existente."
)
async def delete_policy(sp_id: str, service: SecurityPolicyService = Depends(get_security_policy_service)):
    return await service.delete_policy(sp_id)