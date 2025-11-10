"""
Django management command to run inventory sync agent.
"""

from django.core.management.base import BaseCommand
from agents.inventory_sync_agent import run_inventory_sync


class Command(BaseCommand):
    help = 'Synchronize inventory across channels and manage reservations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order_id',
            type=str,
            help='Order ID to reserve/release inventory for'
        )
        parser.add_argument(
            '--product_sku',
            type=str,
            help='Specific product SKU to sync'
        )
        parser.add_argument(
            '--operation',
            type=str,
            choices=['reserve', 'release', 'sync'],
            default='sync',
            help='Operation to perform (default: sync)'
        )
        parser.add_argument(
            '--quantity',
            type=int,
            help='Quantity to reserve/release (uses order quantity if not specified)'
        )
        parser.add_argument(
            '--dry_run',
            action='store_true',
            default=False,
            help='Simulate operations without making actual changes'
        )

    def handle(self, *args, **options):
        order_id = options.get('order_id')
        product_sku = options.get('product_sku')
        operation = options['operation']
        quantity = options.get('quantity')
        dry_run = options['dry_run']

        # Validate arguments
        if operation in ['reserve', 'release'] and not order_id:
            self.stderr.write(
                self.style.ERROR('--order_id is required for reserve/release operations')
            )
            return 1

        if operation == 'sync' and not product_sku and not order_id:
            # Full sync if no specific product/order specified
            pass

        operation_desc = f"{operation} inventory"
        if order_id:
            operation_desc += f" for order {order_id}"
        elif product_sku:
            operation_desc += f" for product {product_sku}"
        else:
            operation_desc += " (full sync)"

        if dry_run:
            operation_desc += " (DRY RUN)"

        self.stdout.write(
            self.style.SUCCESS(f'Starting inventory sync: {operation_desc}...')
        )

        try:
            result = run_inventory_sync(
                order_id=order_id,
                product_sku=product_sku,
                quantity=quantity,
                operation=operation,
                dry_run=dry_run
            )

            if result['status'] in ['SUCCESS', 'COMPLETED', 'PARTIAL_SUCCESS']:
                self.stdout.write(
                    self.style.SUCCESS(f'Inventory sync completed: {result.get("message", "Success")}')
                )

                # Show detailed results
                if 'reservations' in result:
                    self.stdout.write(f"Reservations made: {len(result['reservations'])}")
                if 'released_reservations' in result:
                    self.stdout.write(f"Reservations released: {result['released_reservations']}")
                if 'synced_products' in result:
                    self.stdout.write(f"Products synced: {result['synced_products']}")
                if 'failed_products' in result:
                    self.stdout.write(
                        self.style.WARNING(f"Products failed: {result['failed_products']}")
                    )
                if 'failed_items' in result:
                    self.stdout.write(
                        self.style.WARNING(f"Items failed: {len(result['failed_items'])}")
                    )

                self.stdout.write(f"TaskRun ID: {result.get('task_run_id')}")

                # Return appropriate exit code
                if result['status'] == 'PARTIAL_SUCCESS':
                    return 2  # Partial success
                return 0

            else:
                self.stdout.write(
                    self.style.ERROR(f'Inventory sync failed: {result.get("error")}')
                )
                self.stdout.write(f"Error Type: {result.get('error_type')}")
                return 1

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Inventory sync failed with exception: {e}')
            )
            return 1
