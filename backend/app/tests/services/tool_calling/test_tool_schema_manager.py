import unittest
from backend.app.services.tool_calling.tool_schema_manager import ToolSchemaManager
from backend.app.models.tool_calling_models import ToolSchema

class TestToolSchemaManager(unittest.TestCase):

    def setUp(self):
        self.manager = ToolSchemaManager()
        self.get_weather_schema: ToolSchema = {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The city and state, e.g. San Francisco, CA"},
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
            },
            "required": ["location"]
        }

    def test_get_existing_schema(self):
        schema = self.manager.get_schema("get_weather")
        self.assertIsNotNone(schema)
        self.assertEqual(schema, self.get_weather_schema)

    def test_get_nonexistent_schema(self):
        schema = self.manager.get_schema("get_nonexistent_tool")
        self.assertIsNone(schema)

    def test_register_new_schema(self):
        new_schema: ToolSchema = {
            "type": "object",
            "properties": {"param1": {"type": "string"}},
            "required": ["param1"]
        }
        self.manager.register_schema("new_tool", new_schema)
        retrieved_schema = self.manager.get_schema("new_tool")
        self.assertIsNotNone(retrieved_schema)
        self.assertEqual(retrieved_schema, new_schema)

    def test_register_overwrite_schema(self):
        original_schema: ToolSchema = {
            "type": "object",
            "properties": {"original_param": {"type": "boolean"}}
        }
        self.manager.register_schema("overwrite_tool", original_schema)

        new_schema: ToolSchema = {
            "type": "object",
            "properties": {"new_param": {"type": "number"}}
        }
        self.manager.register_schema("overwrite_tool", new_schema)

        retrieved_schema = self.manager.get_schema("overwrite_tool")
        self.assertIsNotNone(retrieved_schema)
        self.assertEqual(retrieved_schema, new_schema)
        self.assertNotEqual(retrieved_schema, original_schema)

    def test_load_schemas_from_config_placeholder(self):
        # Test that the method exists and can be called without error
        try:
            self.manager.load_schemas_from_config("dummy_path.json")
        except Exception as e:
            self.fail(f"load_schemas_from_config raised an exception: {e}")

if __name__ == '__main__':
    unittest.main()
create_file_with_block
backend/app/tests/services/tool_calling/test_validation_service.py
import unittest
import logging
from backend.app.services.tool_calling.validation_service import ValidationService
from backend.app.models.tool_calling_models import ToolSchema

# Disable logging for tests to keep output clean, unless specifically testing logging
logging.disable(logging.CRITICAL)

class TestValidationService(unittest.TestCase):

    def setUp(self):
        self.service = ValidationService()
        self.sample_schema: ToolSchema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
            # additionalProperties is not set, defaults to True (allows extra fields)
        }
        self.sample_schema_strict: ToolSchema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"],
            "additionalProperties": False
        }

    def test_validate_accumulated_arguments_valid(self):
        data = {"name": "Jules", "age": 30}
        is_valid, error_message = self.service.validate_accumulated_arguments(self.sample_schema, data)
        self.assertTrue(is_valid)
        self.assertIsNone(error_message)

    def test_validate_accumulated_arguments_invalid_type(self):
        data = {"name": "Jules", "age": "thirty"} # age should be integer
        is_valid, error_message = self.service.validate_accumulated_arguments(self.sample_schema, data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_message)
        self.assertIn("'thirty' is not of type 'integer'", error_message)

    def test_validate_accumulated_arguments_missing_required(self):
        data = {"age": 30} # name is missing
        is_valid, error_message = self.service.validate_accumulated_arguments(self.sample_schema, data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_message)
        self.assertIn("'name' is a required property", error_message)

    def test_validate_accumulated_arguments_unexpected_field_allowed_by_default(self):
        data = {"name": "Jules", "city": "Paris"} # city is an additional property
        # Default jsonschema behavior allows additional properties
        is_valid, error_message = self.service.validate_accumulated_arguments(self.sample_schema, data)
        self.assertTrue(is_valid)
        self.assertIsNone(error_message)

    def test_validate_accumulated_arguments_unexpected_field_disallowed(self):
        data = {"name": "Jules", "city": "Paris"} # city is an additional property
        is_valid, error_message = self.service.validate_accumulated_arguments(self.sample_schema_strict, data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_message)
        self.assertIn("Additional properties are not allowed ('city' was unexpected)", error_message)


    def test_validate_tool_call_valid(self):
        data = {"name": "Vincent", "age": 33}
        is_valid, error_message = self.service.validate_tool_call(self.sample_schema, data)
        self.assertTrue(is_valid)
        self.assertIsNone(error_message)

    def test_validate_tool_call_invalid_missing_required(self):
        data = {"age": 33}
        is_valid, error_message = self.service.validate_tool_call(self.sample_schema, data)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_message)
        self.assertIn("'name' is a required property", error_message)

    def test_validate_argument_chunk_simple_string_valid(self):
        schema_subset: ToolSchema = {"type": "string"}
        chunk = "hello"
        is_valid, error_message = self.service.validate_argument_chunk(schema_subset, chunk)
        self.assertTrue(is_valid)
        self.assertIsNone(error_message)

    def test_validate_argument_chunk_simple_integer_invalid_type(self):
        schema_subset: ToolSchema = {"type": "integer"}
        chunk = "hello" # Not an integer
        is_valid, error_message = self.service.validate_argument_chunk(schema_subset, chunk)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_message)
        self.assertIn("'hello' is not of type 'integer'", error_message)

    def test_validate_argument_chunk_object_valid(self):
        schema_subset: ToolSchema = {"type": "object", "properties": {"value": {"type": "number"}}}
        chunk = {"value": 123}
        is_valid, error_message = self.service.validate_argument_chunk(schema_subset, chunk)
        self.assertTrue(is_valid)
        self.assertIsNone(error_message)

    def test_validate_argument_chunk_object_invalid_type_in_property(self):
        schema_subset: ToolSchema = {"type": "object", "properties": {"value": {"type": "number"}}}
        chunk = {"value": "abc"} # value should be number
        is_valid, error_message = self.service.validate_argument_chunk(schema_subset, chunk)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_message)
        self.assertIn("'abc' is not of type 'number'", error_message)
    
    def test_validate_argument_chunk_with_enum_valid(self):
        schema_subset: ToolSchema = {"type": "string", "enum": ["celsius", "fahrenheit"]}
        chunk = "celsius"
        is_valid, error_message = self.service.validate_argument_chunk(schema_subset, chunk)
        self.assertTrue(is_valid)
        self.assertIsNone(error_message)

    def test_validate_argument_chunk_with_enum_invalid(self):
        schema_subset: ToolSchema = {"type": "string", "enum": ["celsius", "fahrenheit"]}
        chunk = "kelvin"
        is_valid, error_message = self.service.validate_argument_chunk(schema_subset, chunk)
        self.assertFalse(is_valid)
        self.assertIsNotNone(error_message)
        self.assertIn("'kelvin' is not one of ['celsius', 'fahrenheit']", error_message)


if __name__ == '__main__':
    unittest.main()
