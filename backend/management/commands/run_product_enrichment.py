"""
Django management command to run product enrichment agent.
"""

from django.core.management.base import BaseCommand
from agents.product_enrichment_agent import run_product_enrichment


class Command(BaseCommand):
    help = 'Enrich product data using AI content generation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--product_id',
            type=str,
            required=True,
            help='Product ID to enrich'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Force re-enrichment even if product was recently enriched'
        )
        parser.add_argument(
            '--dry_run',
            action='store_true',
            default=False,
            help='Simulate enrichment without saving changes'
        )

    def handle(self, *args, **options):
        product_id = options['product_id']
        force = options['force']
        dry_run = options['dry_run']

        operation_desc = f"enriching product {product_id}"
        if force:
            operation_desc += " (forced)"
        if dry_run:
            operation_desc += " (DRY RUN)"

        self.stdout.write(
            self.style.SUCCESS(f'Starting product enrichment: {operation_desc}...')
        )

        try:
            result = run_product_enrichment(
                product_id=product_id,
                force=force,
                dry_run=dry_run
            )

            if result['status'] == 'SUCCESS':
                self.stdout.write(
                    self.style.SUCCESS('Product enrichment completed successfully!')
                )
                self.stdout.write(f"Product ID: {result.get('product_id')}")
                self.stdout.write(f"Enriched Title: {result.get('enriched_title', 'N/A')}")
                self.stdout.write(f"Content Quality Score: {result.get('content_quality_score', 0):.2f}")
                self.stdout.write(f"Tokens Used: {result.get('tokens_used', 0)}")
                if result.get('cached'):
                    self.stdout.write(
                        self.style.WARNING('Note: Used cached enrichment result')
                    )
                self.stdout.write(f"TaskRun ID: {result.get('task_run_id')}")

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING('DRY RUN: No actual changes were made')
                    )

                return 0

            else:
                self.stdout.write(
                    self.style.ERROR(f'Product enrichment failed: {result.get("error")}')
                )
                self.stdout.write(f"Error Type: {result.get('error_type')}")
                return 1

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Product enrichment failed with exception: {e}')
            )
            return 1
