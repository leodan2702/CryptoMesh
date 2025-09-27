import time as T
from typing import List
import ast
from datetime import datetime, timezone

from cryptomesh.models import ActiveObjectModel, FunctionModel, ParameterSpec
from cryptomesh.repositories.activeobjects_repository import ActiveObjectsRepository
from cryptomesh.log.logger import get_logger
from cryptomesh.errors import (
    CryptoMeshError,
    NotFoundError,
    ValidationError,
    CreationError,
)

L = get_logger(__name__)


class ActiveObjectsService:
    """
    Servicio encargado de gestionar los Active Objects en la base de datos.
    """

    def __init__(self, repository: ActiveObjectsRepository):
        self.repository = repository

    # ----------------------------
    # Helpers
    # ----------------------------
    @staticmethod
    def normalize_functions(functions) -> List[dict]:
        """
        Asegura que todos los elementos sean FunctionModel y devuelve dicts listos para Mongo.
        """
        normalized = []
        for f in functions:
            if isinstance(f, FunctionModel):
                normalized.append(f.model_dump(exclude_none=True))
            elif isinstance(f, dict):
                normalized.append(FunctionModel(**f).model_dump(exclude_none=True))
            else:
                raise TypeError(f"Invalid function type: {type(f)}")
        return normalized

    async def create_active_object(self, active_object: ActiveObjectModel) -> ActiveObjectModel:
        t1 = T.time()
        if await self.repository.get_by_id(active_object.active_object_id, id_field="active_object_id"):
            elapsed = round(T.time() - t1, 4)
            L.error({
                "event": "ACTIVE_OBJECT.CREATE.FAIL",
                "reason": "Already exists",
                "active_object_id": active_object.active_object_id,
                "time": elapsed
            })
            raise ValidationError(f"ActiveObject '{active_object.active_object_id}' already exists")

        if active_object.axo_code:
            try:
                # Generar axo_schema y functions
                active_object.axo_schema = self.extract_schema_from_code(active_object.axo_code)
                functions = self.extract_functions_from_code(active_object.axo_code)
                active_object.functions = [
                    f if isinstance(f, FunctionModel) else FunctionModel(**f)
                    for f in functions
                ]
            except Exception as e:
                elapsed = round(T.time() - t1, 4)
                L.error({
                    "event": "ACTIVE_OBJECT.CREATE.FAIL",
                    "reason": str(e),
                    "active_object_id": active_object.active_object_id,
                    "time": elapsed
                })
                raise CryptoMeshError(f"Failed to create ActiveObject '{active_object.active_object_id}': {str(e)}")


        created = await self.repository.create(active_object)
        elapsed = round(T.time() - t1, 4)

        if not created:
            raise CreationError(f"Failed to create ActiveObject '{active_object.active_object_id}'")

        L.info({
            "event": "ACTIVE_OBJECT.CREATED",
            "active_object_id": active_object.active_object_id,
            "time": elapsed
        })
        return created

    async def list_active_objects(self) -> List[ActiveObjectModel]:
        aos = await self.repository.get_all()
        for ao in aos:
            if ao.functions:
                ao.functions = [
                    f if isinstance(f, FunctionModel) else FunctionModel(**f)
                    for f in ao.functions
                ]
        return aos

    async def get_active_object(self, active_object_id: str) -> ActiveObjectModel:
        ao = await self.repository.get_by_id(active_object_id, id_field="active_object_id")
        if not ao:
            raise NotFoundError(active_object_id)

        if ao.functions:
            ao.functions = [
                f if isinstance(f, FunctionModel) else FunctionModel(**f)
                for f in ao.functions
            ]
        return ao

    async def update_active_object(self, active_object_id: str, updates: dict) -> ActiveObjectModel:
        ao_exist = await self.repository.get_by_id(active_object_id, id_field="active_object_id")
        if not ao_exist:
            raise NotFoundError(active_object_id)

        if "axo_code" in updates and updates["axo_code"]:
            try:
                updates["axo_schema"] = self.extract_schema_from_code(updates["axo_code"])
                functions = self.extract_functions_from_code(updates["axo_code"])
                updates["functions"] = self.normalize_functions(functions)
            except Exception as e:
                raise CryptoMeshError(f"Failed to update ActiveObject '{active_object_id}': {str(e)}")

        updated = await self.repository.update({"active_object_id": active_object_id}, updates)
        if not updated:
            raise CryptoMeshError(f"Failed to update ActiveObject '{active_object_id}'")
        return updated

    async def delete_active_object(self, active_object_id: str) -> dict:
        if not await self.repository.get_by_id(active_object_id, id_field="active_object_id"):
            raise NotFoundError(active_object_id)
        success = await self.repository.delete({"active_object_id": active_object_id})
        if not success:
            raise CryptoMeshError(f"Failed to delete ActiveObject '{active_object_id}'")
        return {"detail": f"ActiveObject '{active_object_id}' deleted"}

    async def list_by_microservice(self, microservice_id: str) -> List[ActiveObjectModel]:
        return await self.repository.get_by_filter({"axo_microservice_id": microservice_id})

    @staticmethod
    def extract_schema_from_code(code: str) -> dict:
        """
        Extrae un esquema estructurado de parámetros desde el código.
        Devuelve un dict con init y métodos (cada uno con lista de parámetros).
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValidationError(f"Invalid axo_code syntax: {e}")

        schema = {"init": [], "methods": {}}

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for func in node.body:
                    if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        params = []
                        total_args = func.args.args
                        defaults = func.args.defaults
                        num_required = len(total_args) - len(defaults)

                        for i, arg in enumerate(total_args):
                            if arg.arg == "self":
                                continue

                            # Tipo por annotation si existe
                            param_type = "Any"
                            if arg.annotation:
                                param_type = getattr(arg.annotation, "id", None) or "Any"

                            # Default y required
                            default_value = None
                            required = True
                            if i >= num_required:
                                default_index = i - num_required
                                default_node = defaults[default_index]
                                try:
                                    default_value = ast.literal_eval(default_node)
                                    required = False
                                except Exception:
                                    default_value = None

                            params.append(ParameterSpec(
                                name=arg.arg,
                                type=param_type,
                                description=None,  # luego puedes enriquecer con docstrings
                                required=required,
                                default=default_value
                            ).model_dump())

                        if func.name == "__init__":
                            schema["init"] = params
                        else:
                            schema["methods"][func.name] = params

        return schema


    @staticmethod
    def extract_functions_from_code(code: str) -> List[FunctionModel]:
        """
        Convierte funciones de un OA en FunctionModel con init_params + call_params.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValidationError(f"Invalid axo_code syntax: {e}")

        functions: List[FunctionModel] = []
        init_params: List[ParameterSpec] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                for func in node.body:
                    if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        params: List[ParameterSpec] = []
                        total_args = func.args.args
                        defaults = func.args.defaults
                        num_required = len(total_args) - len(defaults)

                        for i, arg in enumerate(total_args):
                            if arg.arg == "self":
                                continue

                            # Tipo por annotation
                            param_type = "Any"
                            if arg.annotation:
                                param_type = getattr(arg.annotation, "id", None) or "Any"

                            # Default y required
                            default_value = None
                            required = True
                            if i >= num_required:
                                default_index = i - num_required
                                default_node = defaults[default_index]
                                try:
                                    default_value = ast.literal_eval(default_node)
                                    required = False
                                except Exception:
                                    default_value = None

                            params.append(ParameterSpec(
                                name=arg.arg,
                                type=param_type,
                                description=None,
                                required=required,
                                default=default_value
                            ))

                        if func.name == "__init__":
                            init_params = params
                        else:
                            functions.append(
                                FunctionModel(
                                    name=func.name,
                                    init_params=init_params,
                                    call_params=params
                                )
                            )

        return functions
