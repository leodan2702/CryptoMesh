import pytest
from cryptomesh.policies import CMPolicyManager
from cryptomesh.models import PolicyModel, ServiceModel, MicroserviceModel, FunctionModel, Resource


def test_policy_manager():
    pm = CMPolicyManager()
    policy = pm.interpret()

    assert policy.cryptomesh == "v1"
    assert isinstance(policy.services, dict)
    assert len(policy.services) > 0

    for service_id, service in policy.services.items():
        assert isinstance(service_id, str)
        assert isinstance(service, ServiceModel)
        assert isinstance(service.security_policy.roles, list)

        assert isinstance(service.microservices, dict)
        assert len(service.microservices) > 0

        for ms_id, micro in service.microservices.items():
            assert isinstance(ms_id, str)
            assert isinstance(micro, MicroserviceModel)
            assert isinstance(micro.resources, Resource)
            assert isinstance(micro.functions, dict)
            assert len(micro.functions) > 0

            for fn_id, fn in micro.functions.items():
                assert isinstance(fn, FunctionModel)
                assert fn.image.endswith(".encrypt") or fn.image.startswith("rory:")


    
