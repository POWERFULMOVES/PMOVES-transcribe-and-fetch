import logging
from typing import Dict, Any, Optional, Tuple
import jsonschema
from jsonschema.exceptions import (
    ValidationError as JSONSchemaValidationError,
)  # Alias to avoid confusion
from ...models.tool_calling_models import ToolSchema


class ValidationService:
    def __init__(self):
        """
        Initializes the ValidationService.
        """
        self.logger = logging.getLogger(__name__)

    def validate_argument_chunk(
        self, schema_subset: Dict[str, Any], chunk: Any
    ) -> Tuple[bool, Optional[str]]:
        """
        Performs partial validation of a given chunk against a schema_subset.
        For now, this attempts direct validation of the chunk against the subset.
        This is most effective if the chunk itself is expected to be a complete
        JSON structure that the schema_subset describes (e.g., a specific object
        within a larger schema). For primitive types, it will act as a type check.
        """
        try:
            jsonschema.validate(instance=chunk, schema=schema_subset)
            self.logger.debug(
                f"Chunk validation successful against schema: {schema_subset}"
            )
            return True, None
        except JSONSchemaValidationError as e:
            self.logger.warning(
                f"Chunk validation failed: {e.message}. Chunk: {chunk}, Schema: {schema_subset}"
            )
            return False, e.message
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred during chunk validation: {e}. Chunk: {chunk}, Schema: {schema_subset}"
            )
            return False, str(e)

    def validate_accumulated_arguments(
        self, full_schema: ToolSchema, accumulated_args: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates the fully accumulated_args against the full_schema for the tool.
        """
        try:
            jsonschema.validate(instance=accumulated_args, schema=full_schema)
            self.logger.debug(
                f"Accumulated arguments validation successful against schema: {full_schema}"
            )
            return True, None
        except JSONSchemaValidationError as e:
            self.logger.warning(
                f"Accumulated arguments validation failed: {e.message}. Args: {accumulated_args}, Schema: {full_schema}"
            )
            return False, e.message
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred during accumulated arguments validation: {e}. Args: {accumulated_args}, Schema: {full_schema}"
            )
            return False, str(e)

    def validate_tool_call(
        self, tool_schema: ToolSchema, all_args: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validates the complete set of arguments for a tool call against the tool_schema.
        This is similar to validate_accumulated_arguments.
        """
        try:
            jsonschema.validate(instance=all_args, schema=tool_schema)
            self.logger.debug(
                f"Tool call validation successful against schema: {tool_schema}"
            )
            return True, None
        except JSONSchemaValidationError as e:
            self.logger.warning(
                f"Tool call validation failed: {e.message}. Args: {all_args}, Schema: {tool_schema}"
            )
            return False, e.message
        except Exception as e:
            self.logger.error(
                f"An unexpected error occurred during tool call validation: {e}. Args: {all_args}, Schema: {tool_schema}"
            )
            return False, str(e)
