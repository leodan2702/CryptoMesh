import pytest
from cryptomesh.dtos.security_policy_dto import SecurityPolicyDTO, SecurityPolicyUpdateDTO, SecurityPolicyResponseDTO

# -------------------------------
# TEST: Crear política de seguridad
# -------------------------------
@pytest.mark.asyncio
async def test_create_security_policy(client):
    dto = SecurityPolicyDTO(
        roles=["security_manager"],
        requires_authentication=True
    )
    response = await client.post("/api/v1/security-policies/", json=dto.model_dump())
    assert response.status_code == 201, f"Error: {response.json()}"
    data = response.json()
    assert data["roles"] == dto.roles
    assert data["requires_authentication"] == dto.requires_authentication
    assert "sp_id" in data

# -------------------------------
# TEST: Crear política duplicada
# -------------------------------
@pytest.mark.asyncio
async def test_create_duplicate_security_policy(client):
    dto = SecurityPolicyDTO(
        roles=["duplicate_role"],
        requires_authentication=True
    )

    # Primer POST
    res1 = await client.post("/api/v1/security-policies/", json=dto.model_dump())
    assert res1.status_code == 201
    policy_id = res1.json()["sp_id"]

    # Segundo POST (duplicado)
    res2 = await client.post("/api/v1/security-policies/", json=dto.model_dump())
    assert res2.status_code == 201
    assert res2.json()["sp_id"] != policy_id  # Debe generar un nuevo ID

# -------------------------------
# TEST: Obtener política existente
# -------------------------------
@pytest.mark.asyncio
async def test_get_security_policy(client):
    create_dto = SecurityPolicyDTO(
        roles=["ml1_analyst"],
        requires_authentication=True
    )
    create_res = await client.post("/api/v1/security-policies/", json=create_dto.model_dump())
    assert create_res.status_code == 201
    policy_id = create_res.json()["sp_id"]

    response = await client.get(f"/api/v1/security-policies/{policy_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["sp_id"] == policy_id
    assert data["roles"] == create_dto.roles
    assert data["requires_authentication"] == create_dto.requires_authentication

# -------------------------------
# TEST: Actualizar política
# -------------------------------
@pytest.mark.asyncio
async def test_update_security_policy(client):
    create_dto = SecurityPolicyDTO(
        roles=["security_manager"],
        requires_authentication=True
    )
    create_res = await client.post("/api/v1/security-policies/", json=create_dto.model_dump())
    policy_id = create_res.json()["sp_id"]

    update_dto = SecurityPolicyUpdateDTO(
        roles=["ml1_analyst"],
        requires_authentication=False
    )

    update_data = update_dto.model_dump(exclude_unset=True)

    response = await client.put(
        f"/api/v1/security-policies/{policy_id}",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["roles"] == update_dto.roles
    assert data["requires_authentication"] == update_dto.requires_authentication

# -------------------------------
# TEST: Eliminar política
# -------------------------------
@pytest.mark.asyncio
async def test_delete_security_policy(client):
    create_dto = SecurityPolicyDTO(
        roles=["temp_role"],
        requires_authentication=False
    )
    create_res = await client.post("/api/v1/security-policies/", json=create_dto.model_dump())
    policy_id = create_res.json()["sp_id"]

    delete_res = await client.delete(f"/api/v1/security-policies/{policy_id}")
    assert delete_res.status_code == 204

    get_res = await client.get(f"/api/v1/security-policies/{policy_id}")
    assert get_res.status_code == 404


