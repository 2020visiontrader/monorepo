"""
Demo CLI command for end-to-end run through
"""
from django.core.management.base import BaseCommand
from django.core.management import call_command
from brands.models import Brand, BrandProfile
from content.models import ProductDraft, ContentVariant
from store_templates.models import Template, TemplateVariant
from brands.models import Blueprint
from core.models import BackgroundJob
from competitors.models import CompetitorProfile
import uuid


class Command(BaseCommand):
    help = 'Run end-to-end demo: generate insights, blueprint, content, SEO, apply template'

    def add_arguments(self, parser):
        parser.add_argument(
            '--brand',
            type=str,
            default='demo-brand-a',
            help='Brand slug to use (default: demo-brand-a)',
        )

    def handle(self, *args, **options):
        brand_slug = options['brand']
        
        try:
            brand = Brand.objects.get(slug=brand_slug)
        except Brand.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Brand "{brand_slug}" not found'))
            self.stdout.write(self.style.WARNING('Available brands:'))
            for b in Brand.objects.all():
                self.stdout.write(f'  - {b.slug}')
            return 1
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Demo Run Through: {brand.name} ===\n'))
        
        summary = {
            'brand': brand.name,
            'job_ids': [],
            'blueprint_version': None,
            'accepted_variants': 0,
            'rejected_variants': 0,
            'products_processed': 0,
        }
        
        # Step 1: Mock competitor insights (already exists or create)
        self.stdout.write('1. Checking competitor insights...')
        competitors = CompetitorProfile.objects.filter(brand=brand)
        if competitors.exists():
            self.stdout.write(self.style.SUCCESS(f'   ✓ Found {competitors.count()} competitor(s)'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠ No competitors found (skipping)'))
        
        # Step 2: Generate/check blueprint
        self.stdout.write('\n2. Checking blueprint...')
        blueprint = Blueprint.objects.filter(brand=brand).order_by('-version').first()
        if blueprint:
            summary['blueprint_version'] = blueprint.version
            self.stdout.write(self.style.SUCCESS(f'   ✓ Blueprint exists (v{blueprint.version})'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠ No blueprint found (create one manually)'))
        
        # Step 3: Generate content variants for 2 products
        self.stdout.write('\n3. Generating content variants...')
        products = ProductDraft.objects.filter(brand=brand)[:2]
        if not products.exists():
            self.stdout.write(self.style.ERROR('   ✗ No products found'))
            return 1
        
        summary['products_processed'] = products.count()
        self.stdout.write(f'   Processing {products.count()} product(s)...')
        
        for product in products:
            # Mock content generation (create variants directly)
            for field in ['title', 'description']:
                for variant_num in range(1, 4):  # 3 variants
                    variant, created = ContentVariant.objects.get_or_create(
                        product_draft=product,
                        field_name=field,
                        variant_number=variant_num,
                        defaults={
                            'content': f'{field.capitalize()} variant {variant_num} for {product.original_title}',
                            'is_accepted': False,
                            'is_rejected': False,
                        }
                    )
                    if created:
                        self.stdout.write(f'   ✓ Created variant for {product.original_title} - {field}')
        
        # Step 4: Bulk accept first variant for each product field
        self.stdout.write('\n4. Bulk accepting first variants...')
        accepted_count = 0
        for product in products:
            for field in ['title', 'description']:
                variant = ContentVariant.objects.filter(
                    product_draft=product,
                    field_name=field,
                    variant_number=1
                ).first()
                if variant:
                    variant.is_accepted = True
                    variant.is_rejected = False
                    variant.save()
                    accepted_count += 1
        
        summary['accepted_variants'] = accepted_count
        self.stdout.write(self.style.SUCCESS(f'   ✓ Accepted {accepted_count} variants'))
        
        # Step 5: Mock SEO generation (just log)
        self.stdout.write('\n5. SEO generation (mock)...')
        self.stdout.write(self.style.SUCCESS('   ✓ SEO generated (mock - no actual generation)'))
        
        # Step 6: Apply template variant if available
        self.stdout.write('\n6. Applying template variant...')
        variant = TemplateVariant.objects.filter(brand=brand).first()
        if variant:
            # Create new blueprint version
            current = Blueprint.objects.filter(brand=brand).order_by('-version').first()
            new_version = (current.version + 1) if current else 1
            
            new_blueprint = Blueprint.objects.create(
                brand=brand,
                version=new_version,
                json={
                    **variant.manifest,
                    'applied_from_variant': str(variant.id),
                },
                created_by=None,  # System
            )
            summary['blueprint_version'] = new_version
            self.stdout.write(self.style.SUCCESS(f'   ✓ Applied template variant (blueprint v{new_version})'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠ No template variant found (skipping)'))
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        self.stdout.write(f'Brand: {summary["brand"]}')
        self.stdout.write(f'Products processed: {summary["products_processed"]}')
        self.stdout.write(f'Variants accepted: {summary["accepted_variants"]}')
        self.stdout.write(f'Variants rejected: {summary["rejected_variants"]}')
        if summary['blueprint_version']:
            self.stdout.write(f'Blueprint version: {summary["blueprint_version"]}')
        if summary['job_ids']:
            self.stdout.write(f'Job IDs: {", ".join(summary["job_ids"])}')
        else:
            self.stdout.write('Job IDs: (none - mock run)')
        
        self.stdout.write(self.style.SUCCESS('\n✓ Demo run completed successfully!'))
        return 0

