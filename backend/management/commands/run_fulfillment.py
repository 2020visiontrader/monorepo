"""
Django management command to run fulfillment agent.
"""

from django.core.management.base import BaseCommand
from agents.fulfillment_agent import run_fulfillment


class Command(BaseCommand):
    help = 'Process order fulfillment including shipping label generation and carrier integration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order_id',
            type=str,
            required=True,
            help='Order ID to fulfill'
        )
        parser.add_argument(
            '--carrier',
            type=str,
            choices=['fedex', 'ups', 'usps'],
            help='Shipping carrier to use (auto-selected if not specified)'
        )
        parser.add_argument(
            '--service_level',
            type=str,
            choices=['ground', 'express', 'overnight'],
            help='Shipping service level (auto-selected if not specified)'
        )
        parser.add_argument(
            '--dry_run',
            action='store_true',
            default=False,
            help='Simulate fulfillment without actual carrier calls or order updates'
        )

    def handle(self, *args, **options):
        order_id = options['order_id']
        carrier = options.get('carrier')
        service_level = options.get('service_level')
        dry_run = options['dry_run']

        operation_desc = f"fulfilling order {order_id}"
        if carrier:
            operation_desc += f" via {carrier.upper()}"
        if service_level:
            operation_desc += f" ({service_level})"
        if dry_run:
            operation_desc += " (DRY RUN)"

        self.stdout.write(
            self.style.SUCCESS(f'Starting fulfillment: {operation_desc}...')
        )

        try:
            result = run_fulfillment(
                order_id=order_id,
                carrier=carrier,
                service_level=service_level,
                dry_run=dry_run
            )

            if result['status'] == 'SUCCESS':
                self.stdout.write(
                    self.style.SUCCESS('Fulfillment completed successfully!')
                )
                self.stdout.write(f"Tracking Number: {result.get('tracking_number')}")
                self.stdout.write(f"Carrier: {result.get('carrier', 'Unknown').upper()}")
                self.stdout.write(f"Service Level: {result.get('service_level', 'Unknown')}")
                self.stdout.write(f"Shipping Cost: ${result.get('shipping_cost', 0):.2f}")
                self.stdout.write(f"Label URL: {result.get('label_url')}")
                if result.get('estimated_delivery'):
                    self.stdout.write(f"Estimated Delivery: {result['estimated_delivery']}")
                self.stdout.write(f"TaskRun ID: {result.get('task_run_id')}")

                if dry_run:
                    self.stdout.write(
                        self.style.WARNING('DRY RUN: No actual fulfillment was performed')
                    )

                return 0

            else:
                self.stdout.write(
                    self.style.ERROR(f'Fulfillment failed: {result.get("error")}')
                )
                self.stdout.write(f"Error Type: {result.get('error_type')}")
                return 1

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Fulfillment failed with exception: {e}')
            )
            return 1
