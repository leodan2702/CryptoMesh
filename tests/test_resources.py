import pytest

def test_resource_validation():
    from cryptomesh.dtos.resources_dto import ResourcesDTO, HTTPException

    # Valid cases
    valid_cases = [
        {"cpu": 1, "ram": "1GB"},
        {"cpu": 2, "ram": "4GB"},
        {"cpu": 4, "ram": "8GB"},
    ]
    for case in valid_cases:
        dto = ResourcesDTO.model_validate(case)
        assert dto.cpu == case["cpu"]
        assert dto.ram == case["ram"]

    # Invalid CPU cases
    invalid_cpu_cases = [
        {"cpu": 0, "ram": "4GB"},   # Below minimum
        {"cpu": 5, "ram": "4GB"},   # Above maximum
        {"cpu": -1, "ram": "4GB"},  # Negative value
    ]
    for case in invalid_cpu_cases:
        with pytest.raises(HTTPException) as exc_info:
            ResourcesDTO(**case)
        assert exc_info.value.status_code == 400

    # Invalid RAM cases
    invalid_ram_cases = [
        {"cpu": 2, "ram": "0GB"},     # Below minimum
        {"cpu": 2, "ram": "9GB"},     # Above maximum
        {"cpu": 2, "ram": "-1GB"},    # Negative value
        {"cpu": 2, "ram": "4"},       # Missing GB suffix
        {"cpu": 2, "ram": "fourGB"},  # Non-numeric
    ]
    for case in invalid_ram_cases:
        with pytest.raises(HTTPException) as exc_info:
            ResourcesDTO(**case)
        assert exc_info.value.status_code == 400