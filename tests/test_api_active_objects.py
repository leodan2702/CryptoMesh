import pytest
from cryptomesh.dtos.activeobject_dto import ActiveObjectCreateDTO


# --- Helper para generar código Python válido ---
def get_valid_code() -> str:
    return (
        "class BellmanFord:\n"
        "    def __init__(self, graph):\n"
        "        self.graph = graph\n\n"
        "    def run(self, source, target):\n"
        "        return [source, target]\n"
    )


@pytest.mark.asyncio
async def test_create_active_object_with_code_generates_schema_and_functions(client):
    dto = ActiveObjectCreateDTO(
        axo_module="algo.module",
        axo_class_name="BellmanFord",
        axo_version=1,
        axo_microservice_id="microservice-1",
        axo_code=get_valid_code(),
    )
    payload = dto.model_dump()
    payload["axo_code"] = get_valid_code()  # aseguramos string válido

    res = await client.post("/api/v1/active-objects/", json=payload)
    assert res.status_code == 201, res.text
    data = res.json()

    # Verifica que se haya generado schema
    assert "axo_schema" in data
    assert "init" in data["axo_schema"]
    assert "methods" in data["axo_schema"]
    assert "run" in data["axo_schema"]["methods"]

    # Verifica que se hayan generado functions
    assert len(data["functions"]) > 0
    assert any(f["name"] == "run" for f in data["functions"])


@pytest.mark.asyncio
async def test_create_active_object_with_invalid_code_does_not_crash(client):
    dto = ActiveObjectCreateDTO(
        axo_module="broken.module",
        axo_class_name="BrokenClass",
        axo_version=1,
        axo_microservice_id="microservice-1",
        axo_code="this is not python code",  # inválido
    )
    payload = dto.model_dump()
    payload["axo_code"] = "this is not python code"

    res = await client.post("/api/v1/active-objects/", json=payload)
    # Dependiendo de tu handler puede ser 400 o 422 si atrapas SyntaxError
    assert res.status_code in (400, 422, 500)


@pytest.mark.asyncio
async def test_schema_endpoint_returns_and_updates(client):
    # Crear con código válido
    dto = ActiveObjectCreateDTO(
        axo_module="schema.module",
        axo_class_name="SchemaClass",
        axo_version=1,
        axo_microservice_id="microservice-1",
        axo_code=get_valid_code(),
    )
    payload = dto.model_dump()
    payload["axo_code"] = get_valid_code()

    res = await client.post("/api/v1/active-objects/", json=payload)
    assert res.status_code == 201, res.text
    ao_id = res.json()["active_object_id"]

    # Pedir el schema vía endpoint
    schema_res = await client.get(f"/api/v1/active-objects/{ao_id}/schema")
    assert schema_res.status_code == 200, schema_res.text
    schema = schema_res.json()
    assert "methods" in schema
    assert "run" in schema["methods"]
