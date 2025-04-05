# cryptomesh/policies/__init__.py

import os
import yaml
from typing import Any, Dict

from cryptomesh.models import (
    PolicyModel,
    ServiceModel,
    MicroserviceModel,
    FunctionModel,
    SecurityPolicy,
    Resource,
    Storage,
    StoragePath,
    ConnectionModel 
)


class CMPolicyManager:
    """
    CMPolicyManager is responsible for managing the policy configuration
    for the CryptoMesh system.
    """

    def __init__(self, policy_file: str = "policies/example_1.yml"):
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

    def interpret(self) -> PolicyModel:
        """
        Interpret the loaded policy configuration and convert it into a PolicyModel object.
        """
        if not self._raw_data:
            self.load_policy()

        services_objs = {}

        for service_id, service_data in self._raw_data["services"].items():
            microservices_objs = {}

            for ms_name, ms_data in service_data.get("microservices", {}).items():
                functions_objs = {
                    fn_name: FunctionModel(**fn_data)
                    for fn_name, fn_data in ms_data.get("functions", {}).items()
                }

                microservices_objs[ms_name] = MicroserviceModel(
                    security_policy=SecurityPolicy(**ms_data["security_policy"]),
                    resources=ms_data["resources"],
                    functions=functions_objs,
                )

            services_objs[service_id] = ServiceModel(
                security_policy=SecurityPolicy(**service_data["security_policy"]),
                microservices=microservices_objs,
            )

        connections_objs = [
            ConnectionModel(**conn)
            for conn in self._raw_data.get("connections", [])
        ]

        return PolicyModel(
            cryptomesh=self._raw_data["cryptomesh"],
            services=services_objs,
            connections=connections_objs,
        )
