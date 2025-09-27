from cryptomesh.dtos import SchemaDTO
import ast
from cryptomesh.log.logger import get_logger

L = get_logger(__name__)

class Utils:
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
                        # Get all arguments except for 'self'
                        args = [arg.arg for arg in func.args.args if arg.arg != "self"]
                        
                        if func.name == "__init__":
                            schema.init = args
                        else:
                            schema.methods[func.name] = args
                break  # Only process the first class found (In the future we can support multiple classes)

        return schema