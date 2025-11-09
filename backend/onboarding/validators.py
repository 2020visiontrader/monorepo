"""
JSON schema validators for onboarding data
"""
import json
import os
from pathlib import Path
from typing import Dict, Any
from jsonschema import validate, ValidationError, Draft7Validator
from rest_framework.exceptions import ValidationError as DRFValidationError


SCHEMAS_DIR = Path(__file__).parent / 'schemas'


def load_schema(schema_name: str) -> Dict[str, Any]:
    """Load a JSON schema from the schemas directory"""
    schema_path = SCHEMAS_DIR / f"{schema_name}.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema not found: {schema_name}")

    with open(schema_path, 'r') as f:
        return json.load(f)


def validate_against_schema(data: Dict[str, Any], schema_name: str) -> None:
    """
    Validate data against a JSON schema
    Raises DRFValidationError if validation fails
    """
    try:
        schema = load_schema(schema_name)
        validate(instance=data, schema=schema, cls=Draft7Validator)
    except ValidationError as e:
        raise DRFValidationError({
            'validation_error': str(e.message),
            'field': '.'.join(str(p) for p in e.path) if e.path else 'root',
            'schema': schema_name
        })
    except FileNotFoundError as e:
        raise DRFValidationError({
            'error': f'Schema validation failed: {str(e)}'
        })


def validate_store_settings(data: Dict[str, Any]) -> None:
    """Validate store settings data"""
    validate_against_schema(data, 'store_settings')


def validate_product_priorities(data: Dict[str, Any]) -> None:
    """Validate product priorities data"""
    validate_against_schema(data, 'product_priorities')


def validate_user_consent(data: Dict[str, Any]) -> None:
    """Validate user consent data"""
    validate_against_schema(data, 'user_consent')


def validate_suggestion(data: Dict[str, Any]) -> None:
    """Validate suggestion data"""
    validate_against_schema(data, 'suggestion')


def validate_scan_config(data: Dict[str, Any]) -> None:
    """Validate scan configuration data"""
    validate_against_schema(data, 'scan_config')
