# tests/test_hierarchy.py
import pytest
from cryptomesh.dtos.hierarchy_dto import ServiceHierarchyDTO

@pytest.mark.asyncio
async def test_get_hierarchy(client):
    """
    Comprueba que el endpoint /hierarchy devuelve la jerarquía completa de servicios,
    microservicios y objetos activos con sus métodos.
    """

    # Llamamos al endpoint
    response = await client.get("/api/v1/hierarchy")
    
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    
    # Validamos que cada elemento es un ServiceHierarchyDTO (estructura básica)
    for svc in data:
        assert "service_id" in svc
        assert "service_name" in svc
        assert "microservices" in svc
        assert isinstance(svc["microservices"], list)

        for ms in svc["microservices"]:
            assert "microservice_id" in ms
            assert "microservice_name" in ms
            assert "active_objects" in ms
            assert isinstance(ms["active_objects"], list)

            for ao in ms["active_objects"]:
                assert "active_object_id" in ao
                assert "object_name" in ao
                assert "methods" in ao
                assert isinstance(ao["methods"], list)

                for method in ao["methods"]:
                    assert "name" in method
                    assert "parameters" in method
                    assert isinstance(method["parameters"], list)
