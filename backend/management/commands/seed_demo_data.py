"""
Seed demo data command
"""
from django.core.management.base import BaseCommand
from core.models import Organization, User, RoleAssignment
from brands.models import Brand, BrandProfile
from competitors.models import CompetitorProfile
from content.models import ProductDraft
from store_templates.models import Template
import uuid


class Command(BaseCommand):
    help = 'Seed demo organization, brands, users, and sample data'

    def handle(self, *args, **options):
        # Create organization
        org, created = Organization.objects.get_or_create(
            slug='demo-agency',
            defaults={
                'name': 'Demo Agency',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created organization: {org.name}'))
        org_count = Organization.objects.count()

        # Create users
        admin_user, created = User.objects.get_or_create(
            email='admin@demo.com',
            defaults={
                'username': 'admin',
                'organization': org,
            }
        )
        if created:
            admin_user.set_password('password123!')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin_user.email}'))
        
        editor_user, created = User.objects.get_or_create(
            email='editor@demo.com',
            defaults={
                'username': 'editor',
                'organization': org,
            }
        )
        if created:
            editor_user.set_password('password123!')
            editor_user.save()
            self.stdout.write(self.style.SUCCESS(f'Created editor user: {editor_user.email}'))
        
        # Create role assignments
        RoleAssignment.objects.get_or_create(
            user=admin_user,
            organization=org,
            defaults={'role': 'ORG_ADMIN'}
        )
        
        RoleAssignment.objects.get_or_create(
            user=editor_user,
            organization=org,
            defaults={'role': 'EDITOR'}
        )

        # Create brands
        brand_a, created = Brand.objects.get_or_create(
            organization=org,
            slug='demo-brand-a',
            defaults={
                'name': 'Demo Brand A',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created brand: {brand_a.name}'))
        
        brand_b, created = Brand.objects.get_or_create(
            organization=org,
            slug='demo-brand-b',
            defaults={
                'name': 'Demo Brand B',
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created brand: {brand_b.name}'))

        # Create brand profiles
        profile_a, created = BrandProfile.objects.get_or_create(
            brand=brand_a,
            defaults={
                'mission': 'Premium quality products for modern consumers',
                'categories': ['Electronics', 'Home & Garden'],
                'single_sku': False,
            }
        )
        
        profile_b, created = BrandProfile.objects.get_or_create(
            brand=brand_b,
            defaults={
                'mission': 'Single-product excellence',
                'categories': ['Lifestyle'],
                'single_sku': True,  # Single SKU brand
            }
        )

        # Create role assignments for brands
        RoleAssignment.objects.get_or_create(
            user=admin_user,
            organization=org,
            brand_id=brand_a.id,
            defaults={'role': 'BRAND_MANAGER'}
        )
        
        RoleAssignment.objects.get_or_create(
            user=editor_user,
            organization=org,
            brand_id=brand_a.id,
            defaults={'role': 'EDITOR'}
        )

        # Create products
        products_a = []
        for i in range(1, 3):
            product, created = ProductDraft.objects.get_or_create(
                brand=brand_a,
                shopify_product_id=f'prod_a_{i}',
                defaults={
                    'original_title': f'Product A{i}',
                    'original_description': f'Description for Product A{i}',
                }
            )
            products_a.append(product)
        
        products_b = []
        for i in range(1, 3):
            product, created = ProductDraft.objects.get_or_create(
                brand=brand_b,
                shopify_product_id=f'prod_b_{i}',
                defaults={
                    'original_title': f'Product B{i}',
                    'original_description': f'Description for Product B{i}',
                }
            )
            products_b.append(product)

        # Create competitors
        competitor_a, created = CompetitorProfile.objects.get_or_create(
            brand=brand_a,
            url='https://example-competitor-a.com',
            defaults={
                'name': 'Competitor A',
                'is_primary': True,
            }
        )
        
        competitor_b, created = CompetitorProfile.objects.get_or_create(
            brand=brand_b,
            url='https://example-competitor-b.com',
            defaults={
                'name': 'Competitor B',
                'is_primary': True,
            }
        )

        # Create templates
        starter_template, created = Template.objects.get_or_create(
            name='Starter Template',
            defaults={
                'complexity': 'Starter',
                'source': 'curated',
                'manifest': {
                    'meta': {
                        'name': 'Starter Template',
                        'description': 'Clean and simple design',
                        'complexity': 'Starter',
                        'tags': ['general'],
                    },
                    'theme_tokens': {
                        'colors': {'primary': '#6366f1'},
                        'typography': {'font_family': 'Inter'},
                    },
                    'sections': [
                        {'key': 'hero', 'name': 'Hero', 'enabled': True},
                        {'key': 'features', 'name': 'Features', 'enabled': True},
                    ],
                },
                'is_active': True,
            }
        )
        
        sophisticated_template, created = Template.objects.get_or_create(
            name='Sophisticated Template',
            defaults={
                'complexity': 'Sophisticated',
                'source': 'curated',
                'manifest': {
                    'meta': {
                        'name': 'Sophisticated Template',
                        'description': 'Advanced template with rich features',
                        'complexity': 'Sophisticated',
                        'tags': ['advanced'],
                    },
                    'theme_tokens': {
                        'colors': {'primary': '#4f46e5', 'secondary': '#7c3aed'},
                        'typography': {'font_family': 'Inter'},
                    },
                    'sections': [
                        {'key': 'hero', 'name': 'Hero', 'enabled': True},
                        {'key': 'features', 'name': 'Features', 'enabled': True},
                        {'key': 'products', 'name': 'Products', 'enabled': True},
                        {'key': 'testimonials', 'name': 'Testimonials', 'enabled': False},
                    ],
                },
                'is_active': True,
            }
        )

        # Summary
        self.stdout.write(self.style.SUCCESS('\n=== Seed Summary ==='))
        self.stdout.write(f'Organizations: {org_count}')
        self.stdout.write(f'Users: {User.objects.filter(organization=org).count()}')
        self.stdout.write(f'Brands: {Brand.objects.filter(organization=org).count()}')
        self.stdout.write(f'Products: {ProductDraft.objects.filter(brand__organization=org).count()}')
        self.stdout.write(f'Competitors: {CompetitorProfile.objects.filter(brand__organization=org).count()}')
        self.stdout.write(f'Templates: {Template.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\nDemo data seeded successfully!'))
        self.stdout.write(self.style.WARNING('⚠️  Demo passwords: password123! (CHANGE IN PRODUCTION)'))
        self.stdout.write(f'Login: admin@demo.com / password123! (ORG_ADMIN)')
        self.stdout.write(f'Login: editor@demo.com / password123! (EDITOR)')

