import pytest
from cryptomesh.utils import Utils
from cryptomesh.dtos import SchemaDTO

def test_extract_schema_with_valid_class():
    """
    Tests that a standard class with __init__ and other methods is parsed correctly.
    """
    # Arrange
    code = """
class DataProcessor:
    def __init__(self, source_bucket: str, source_key: str):
        self.bucket = source_bucket
        self.key = source_key

    def run(self, multiplier: int):
        pass
    
    async def process_async(self, item_id):
        pass
"""
    # Act
    result = Utils.extract_schema_from_code(code)

    # Assert
    assert result.class_name == "DataProcessor"
    assert result.init == ["source_bucket", "source_key"]
    assert "run" in result.methods
    assert result.methods["run"] == ["multiplier"]
    assert "process_async" in result.methods
    assert result.methods["process_async"] == ["item_id"]


def test_extract_schema_no_class_found():
    """
    Tests that the default SchemaDTO is returned if the code contains no class.
    """
    # Arrange
    code_without_class = "def my_function(a, b):\n    return a + b"

    # Act
    result = Utils.extract_schema_from_code(code_without_class)

    # Assert
    assert result.class_name == "AxoObjectClass"
    assert result.init == []
    assert result.methods == {}


def test_extract_schema_with_syntax_error():
    """
    Tests that the default SchemaDTO is returned if the code has a syntax error.
    """
    # Arrange
    invalid_code = "class MyClass:\n  def broken_method("

    # Act
    result = Utils.extract_schema_from_code(invalid_code)

    # Assert
    assert isinstance(result, SchemaDTO)
    assert result.class_name == "AxoObjectClass"
    assert result.init == []
    assert result.methods == {}


def test_extract_schema_only_processes_first_class():
    """
    Tests that only the first class in the code is processed due to the 'break'.
    """
    # Arrange
    code_with_two_classes = """
    class FirstClass:
        def __init__(self, name):
            self.name = name

    class SecondClass:
        def process(self):
            pass
    """
    # Act
    result = Utils.extract_schema_from_code(code_with_two_classes)

    # Assert
    assert result.class_name == "FirstClass"
    assert result.init == ["name"]
    assert "process" not in result.methods


def test_extract_schema_class_with_no_init():
    """
    Tests a class that has methods but no __init__ method.
    """
    # Arrange
    code = """
    class Helper:
        def do_work(self, task_id):
            print(f"Working on {task_id}")
    """
    # Act
    result = Utils.extract_schema_from_code(code)

    # Assert
    assert result.class_name == "Helper"
    assert result.init == [] # Should be an empty list
    assert result.methods["do_work"] == ["task_id"]