"""
Django management command to build and render templates.
"""

from django.core.management.base import BaseCommand
from agents.template_renderer_agent import render_template
import json


class Command(BaseCommand):
    help = 'Build and render a template with context data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--template_id',
            type=int,
            required=True,
            help='ID of the template to build'
        )
        parser.add_argument(
            '--brand_id',
            type=int,
            help='Brand ID for context (optional, will load from DB if not provided)'
        )
        parser.add_argument(
            '--context_file',
            type=str,
            help='JSON file containing context data (optional)'
        )
        parser.add_argument(
            '--target_bucket',
            type=str,
            default='templates-rendered',
            help='Supabase bucket for deployment (default: templates-rendered)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Force re-rendering even if template was recently built'
        )
        parser.add_argument(
            '--output_json',
            action='store_true',
            default=False,
            help='Output result as JSON instead of human-readable text'
        )

    def handle(self, *args, **options):
        template_id = options['template_id']
        brand_id = options.get('brand_id')
        context_file = options.get('context_file')
        target_bucket = options['target_bucket']
        force = options['force']
        output_json = options['output_json']

        self.stdout.write(
            self.style.SUCCESS(f'Starting template build for template ID {template_id}...')
        )

        try:
            # Load context data
            context = self._load_context(brand_id, context_file)

            # Render template
            result = render_template(
                template_id=template_id,
                context=context,
                target_bucket=target_bucket,
                force=force
            )

            if output_json:
                self.stdout.write(json.dumps(result, indent=2))
            else:
                if result.get('success'):
                    self.stdout.write(
                        self.style.SUCCESS('Template build completed successfully!')
                    )
                    self.stdout.write(f"Public URL: {result.get('public_url')}")
                    self.stdout.write(f"Bucket Path: {result.get('bucket_path')}")
                    self.stdout.write(f"Build ID: {result.get('build_id')}")
                    self.stdout.write(f"Rendered Files: {result.get('rendered_files')}")
                    if result.get('cached'):
                        self.stdout.write(
                            self.style.WARNING('Note: Used cached build (use --force to rebuild)')
                        )
                else:
                    self.stdout.write(
                        self.style.ERROR(f'Template build failed: {result.get("error")}')
                    )
                    return

        except Exception as e:
            if output_json:
                self.stdout.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }, indent=2))
            else:
                self.stdout.write(
                    self.style.ERROR(f'Template build failed with exception: {e}')
                )
            raise

    def _load_context(self, brand_id=None, context_file=None):
        """Load context data from file or generate from brand."""
        if context_file:
            # Load from JSON file
            with open(context_file, 'r') as f:
                return json.load(f)

        # Generate default context
        context = {
            'brand': {
                'name': 'Demo Store',
                'tagline': 'Your Store Tagline',
                'description': 'Welcome to our demo store',
                'contact_email': 'contact@example.com'
            },
            'theme': {
                'colors': {
                    'primary': '#007bff',
                    'secondary': '#6c757d'
                },
                'typography': {
                    'font_family': 'Inter, sans-serif'
                }
            },
            'navigation': [
                {'label': 'Home', 'url': '/'},
                {'label': 'Products', 'url': '/products'},
                {'label': 'About', 'url': '/about'},
                {'label': 'Contact', 'url': '/contact'}
            ],
            'hero': {
                'title': 'Welcome to Our Store',
                'subtitle': 'Discover amazing products crafted just for you'
            },
            'products': [
                {
                    'title': 'Premium Product',
                    'description': 'This is a high-quality product that offers exceptional value.',
                    'price': 99.99,
                    'image_url': '/placeholder-product.jpg',
                    'availability': 'in_stock',
                    'category': 'Premium'
                },
                {
                    'title': 'Standard Product',
                    'description': 'A reliable product that meets everyday needs.',
                    'price': 49.99,
                    'image_url': '/placeholder-product.jpg',
                    'availability': 'in_stock',
                    'category': 'Standard'
                },
                {
                    'title': 'Basic Product',
                    'description': 'An affordable option for essential needs.',
                    'price': 19.99,
                    'image_url': '/placeholder-product.jpg',
                    'availability': 'out_of_stock',
                    'category': 'Basic'
                }
            ]
        }

        return context
