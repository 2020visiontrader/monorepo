"""
Django management command to run order processing agent.
"""

from django.core.management.base import BaseCommand
from agents.order_processing_agent import run_order_processing
import uuid


class Command(BaseCommand):
    help = 'Process an e-commerce order through the complete fulfillment workflow'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order_id',
            type=str,
            required=True,
            help='UUID of the order to process'
        )
        parser.add_argument(
            '--idempotency_key',
            type=str,
            help='Idempotency key for safe retries (auto-generated if not provided)'
        )
        parser.add_argument(
            '--skip_payment',
            action='store_true',
            default=False,
            help='Skip payment processing (for testing or manual orders)'
        )
        parser.add_argument(
            '--force_process',
            action='store_true',
            default=False,
            help='Force processing even if order was already processed'
        )
        parser.add_argument(
            '--dry_run',
            action='store_true',
            default=False,
            help='Validate order but do not perform actual processing'
        )

    def handle(self, *args, **options):
        order_id = options['order_id']
        idempotency_key = options.get('idempotency_key')
        skip_payment = options['skip_payment']
        force_process = options['force_process']
        dry_run = options['dry_run']

        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE: No actual processing will be performed')
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting order processing for order {order_id}...'
            )
        )

        try:
            # Generate idempotency key if not provided
            if not idempotency_key:
                idempotency_key = f"cmd_{order_id}_{uuid.uuid4().hex[:8]}"

            result = run_order_processing(
                order_id=order_id,
                idempotency_key=idempotency_key,
                skip_payment=skip_payment or dry_run,
                force_process=force_process
            )

            if result['status'] == 'SUCCESS':
                self.stdout.write(
                    self.style.SUCCESS('Order processing completed successfully!')
                )
                self.stdout.write(f"Order ID: {result.get('order_id')}")
                self.stdout.write(f"Order Status: {result.get('order_status')}")
                self.stdout.write(f"Payment Processed: {result.get('payment_processed')}")
                self.stdout.write(f"Inventory Reserved: {result.get('inventory_reserved')}")
                self.stdout.write(f"Invoice Generated: {result.get('invoice_generated')}")
                self.stdout.write(f"Fulfillment Triggered: {result.get('fulfillment_triggered')}")
                self.stdout.write(f"TaskRun ID: {result.get('task_run_id')}")

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING('DRY RUN: No actual changes were made')
                    )

            else:
                self.stdout.write(
                    self.style.ERROR(f'Order processing failed: {result.get("error")}')
                )
                self.stdout.write(f"Error Type: {result.get('error_type')}")
                return 1

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Order processing failed with exception: {e}')
            )
            return 1

        return 0
