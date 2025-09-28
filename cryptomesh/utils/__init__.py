
import ast
from typing import List, Dict
from pydantic import ValidationError
from cryptomesh.dtos import SchemaDTO
from cryptomesh.log.logger import get_logger
from cryptomesh.dtos import ParameterSpecDTO
from cryptomesh.models import FunctionModel
L = get_logger(__name__)

class Utils:
    @staticmethod
    def _extract_params_from_func(func_node: ast.FunctionDef | ast.AsyncFunctionDef) -> List[ParameterSpecDTO]:
        """
        Private helper to extract a list of ParameterSpec from a function's AST node.
        This centralizes the parameter parsing logic.
        """
        params: List[ParameterSpecDTO] = []
        total_args = func_node.args.args
        defaults = func_node.args.defaults
        num_required = len(total_args) - len(defaults)

        for i, arg in enumerate(total_args):
            if arg.arg == "self":
                continue

            param_type = "Any"
            if arg.annotation:
                param_type = getattr(arg.annotation, 'id', 'Any')

            default_value = None
            is_required = True
            if i >= num_required:
                is_required = False
                default_index = i - num_required
                default_node = defaults[default_index]
                try:
                    default_value = ast.literal_eval(default_node)
                except Exception:
                    # In case the default value is complex (e.g., a function call)
                    default_value = None

            params.append(ParameterSpecDTO(
                name=arg.arg,
                type=param_type,
                required=is_required,
                default=default_value
            ))
        return params


    @staticmethod
    def extract_schema_from_code(code: str)-> SchemaDTO:
        """
        Parses a string of Python code to extract the class name, __init__ args,
        and method signatures.
        """
        # 1. Initialize the schema with the default class name.
        schema = SchemaDTO(
            class_name="GenericActiveObject",
            init=[],
            methods={}
        )

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            L.error({
                "event": "ACTIVE_OBJECT.SCHEMA_EXTRACTION.FAIL",
                "reason": "Syntax error in code",
                "error": str(e)
            })
            return schema
        
        # Iterate through the top-level nodes in the code (e.g., classes, functions)
        # Maybe in the future we can support multiple classes per code sent from UI. 
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                # 2. If a class is found, update the class name in the schema.
                # This will overwrite the default "AxoObjectClass".
                schema.class_name = node.name
                # Continue to extract method details.
                for func in node.body:
                    if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        params = Utils._extract_params_from_func(func)
                        if func.name == "__init__":
                            schema.init = params
                        else:
                            schema.methods[func.name] = params
                break  # Only process the first class found (In the future we can support multiple classes)

        return schema
    @staticmethod
    def extract_functions_from_code(code: str) -> List[FunctionModel]:
        """
        Parses Python code to create a list of executable functions, each bundled
        with the class's __init__ parameters.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValidationError(f"Invalid axo_code syntax: {e}")

        functions: List[FunctionModel] = []
        init_params: List[ParameterSpecDTO] = []

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                # First pass: find __init__ params
                for func in node.body:
                    if isinstance(func, ast.FunctionDef) and func.name == "__init__":
                        init_params = Utils._extract_params_from_func(func)
                        break # Found init, no need to look further in this pass
                
                # Second pass: find other methods and build FunctionModel
                for func in node.body:
                    if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)) and func.name != "__init__":
                        call_params = Utils._extract_params_from_func(func)
                        functions.append(
                            FunctionModel(
                                name=func.name,
                                init_params=init_params,
                                call_params=call_params
                            )
                        )
                break # Process only the first class
        return functions
