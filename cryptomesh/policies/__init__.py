# cryptomesh/policies/__init__.py

import os
import yaml
from typing import Any, Dict

from cryptomesh.models import (
    EndpointModel,
    FunctionModel,
    MicroserviceModel,
    ServiceModel,
)

class CMPolicyManager:
    """
    CMPolicyManager is responsible for managing the policy configuration
    for the CryptoMesh system.
    """
    def __init__(self, policy_file: str):
        self.policy_file = policy_file
        self._raw_data: Dict[str, Any] = {}

    def load_policy(self) -> Dict[str, Any]:
        """
        Load the policy configuration from a YAML file.
        """
        if not os.path.exists(self.policy_file):
            raise FileNotFoundError(f"Policy not found: {self.policy_file}")

        with open(self.policy_file, "r") as f:
            self._raw_data = yaml.safe_load(f)

        return self._raw_data

    def parse(self) -> Dict[str, Dict[str, Any]]:
        if not self._raw_data:
            self.load_policy()
        return {
            "endpoints": self._raw_data.get("endpoints", {}),
            "functions": self._raw_data.get("functions", {}),
            "microservices": self._raw_data.get("microservices", {}),
            "services": self._raw_data.get("services", {}),
        }

    def as_models(self) -> Dict[str, Dict[str, Any]]:
        parsed = self.parse()
        return {
            "endpoints": {
                eid: EndpointModel(endpoint_id=eid, **edata)
                for eid, edata in parsed["endpoints"].items()
            },
            "functions": {
                fid: FunctionModel(function_id=fid, **fdata)
                for fid, fdata in parsed["functions"].items()
            },
            "microservices": {
                msid: MicroserviceModel(microservice_id=msid, **msdata)
                for msid, msdata in parsed["microservices"].items()
            },
            "services": {
                sid: ServiceModel(service_id=sid, **sdata)
                for sid, sdata in parsed["services"].items()
            },
        }
