"""
Management command to validate JSON schemas
"""
import json
from pathlib import Path
from django.core.management.base import BaseCommand
from jsonschema import Draft7Validator, SchemaError


class Command(BaseCommand):
    help = 'Validate all JSON schemas in the onboarding app'

    def handle(self, *args, **options):
        schemas_dir = Path(__file__).parent.parent.parent / 'schemas'

        if not schemas_dir.exists():
            self.stdout.write(self.style.ERROR(f'Schemas directory not found: {schemas_dir}'))
            return

        schema_files = list(schemas_dir.glob('*.json'))

        if not schema_files:
            self.stdout.write(self.style.WARNING('No schema files found'))
            return

        self.stdout.write(self.style.SUCCESS(f'Found {len(schema_files)} schema files'))

        errors = []

        for schema_file in schema_files:
            self.stdout.write(f'Validating {schema_file.name}...')

            try:
                with open(schema_file, 'r') as f:
                    schema = json.load(f)

                # Validate schema itself
                Draft7Validator.check_schema(schema)

                self.stdout.write(self.style.SUCCESS(f'  ✓ {schema_file.name} is valid'))

            except json.JSONDecodeError as e:
                error_msg = f'  ✗ {schema_file.name}: Invalid JSON - {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

            except SchemaError as e:
                error_msg = f'  ✗ {schema_file.name}: Invalid schema - {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

            except Exception as e:
                error_msg = f'  ✗ {schema_file.name}: Error - {str(e)}'
                errors.append(error_msg)
                self.stdout.write(self.style.ERROR(error_msg))

        if errors:
            self.stdout.write(self.style.ERROR(f'\n{len(errors)} schema(s) failed validation'))
            return
        else:
            self.stdout.write(self.style.SUCCESS(f'\nAll {len(schema_files)} schemas are valid!'))
