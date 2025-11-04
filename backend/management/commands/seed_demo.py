"""
Seed demo data
"""
from django.core.management.base import BaseCommand
from core.models import Organization, User
from brands.models import Brand, BrandProfile
from competitors.models import CompetitorProfile
from content.models import ProductDraft
from frameworks.models import Framework
from store_templates.models import Template
import uuid


class Command(BaseCommand):
    help = 'Seed demo organization, brand, and sample data'

    def handle(self, *args, **options):
        # Create organization
        org, created = Organization.objects.get_or_create(
            slug='demo-org',
            defaults={
                'name': 'Demo Organization',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created organization: {org.name}'))

        # Create user
        user, created = User.objects.get_or_create(
            email='demo@example.com',
            defaults={
                'username': 'demo',
                'organization': org,
            }
        )
        if created:
            user.set_password('demo123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.email}'))

        # Create brand
        brand, created = Brand.objects.get_or_create(
            organization=org,
            slug='demo-brand',
            defaults={
                'name': 'Demo Brand',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created brand: {brand.name}'))

        # Create brand profile
        profile, created = BrandProfile.objects.get_or_create(
            brand=brand,
            defaults={
                'mission': 'To provide high-quality products to customers',
                'categories': ['Electronics', 'Home & Garden'],
                'personas': [
                    {'name': 'Tech Enthusiast', 'age': '25-40'},
                    {'name': 'Home Decor Lover', 'age': '30-50'},
                ],
                'tone_sliders': {
                    'professional': 0.8,
                    'friendly': 0.7,
                    'casual': 0.3,
                },
                'required_terms': ['premium', 'quality'],
                'forbidden_terms': ['cheap', 'discount'],
                'single_sku': False,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created brand profile'))

        # Create competitor
        competitor, created = CompetitorProfile.objects.get_or_create(
            brand=brand,
            url='https://example.com',
            defaults={
                'name': 'Example Competitor',
                'is_primary': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created competitor profile'))

        # Create sample products
        for i in range(3):
            ProductDraft.objects.get_or_create(
                brand=brand,
                shopify_product_id=f'prod_{i}',
                defaults={
                    'original_title': f'Sample Product {i + 1}',
                    'original_description': f'This is a sample product description for product {i + 1}',
                }
            )
        self.stdout.write(self.style.SUCCESS('Created sample products'))

        # Create sample frameworks
        frameworks_data = [
            {
                'name': 'AIDA',
                'description': 'Attention, Interest, Desire, Action',
                'slots': [
                    {'name': 'attention', 'type': 'text', 'required': True},
                    {'name': 'interest', 'type': 'text', 'required': True},
                    {'name': 'desire', 'type': 'text', 'required': True},
                    {'name': 'action', 'type': 'text', 'required': True},
                ],
                'output_schema': {'type': 'object', 'properties': {}},
            },
            {
                'name': 'PAS',
                'description': 'Problem, Agitate, Solve',
                'slots': [
                    {'name': 'problem', 'type': 'text', 'required': True},
                    {'name': 'agitate', 'type': 'text', 'required': True},
                    {'name': 'solve', 'type': 'text', 'required': True},
                ],
                'output_schema': {'type': 'object', 'properties': {}},
            },
        ]
        
        for fw_data in frameworks_data:
            Framework.objects.get_or_create(
                name=fw_data['name'],
                defaults=fw_data
            )
        self.stdout.write(self.style.SUCCESS('Created sample frameworks'))

        # Create sample template
        template, created = Template.objects.get_or_create(
            name='Starter Template',
            defaults={
                'complexity': 'Starter',
                'source': 'curated',
                'manifest': {
                    'meta': {
                        'name': 'Starter Template',
                        'description': 'A clean and simple starter template',
                        'complexity': 'Starter',
                        'tags': ['general'],
                    },
                    'theme_tokens': {
                        'colors': {'primary': '#6366f1', 'secondary': '#8b5cf6'},
                        'typography': {'font_family': 'Inter'},
                    },
                    'sections': [
                        {'key': 'hero', 'name': 'Hero', 'enabled': True},
                        {'key': 'features', 'name': 'Features', 'enabled': True},
                    ],
                },
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Created sample template'))

        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS(f'Login with: {user.email} / demo123'))

