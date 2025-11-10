"""
Django management command to run store scraper agent.
"""

from django.core.management.base import BaseCommand
from agents.store_scraper_agent import run_store_scrape
import uuid


class Command(BaseCommand):
    help = 'Run the store scraper agent to extract competitor data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            required=True,
            help='Competitor store URL to scrape'
        )
        parser.add_argument(
            '--brand_id',
            type=str,
            help='Associated brand ID (UUID)'
        )
        parser.add_argument(
            '--render-js',
            action='store_true',
            default=False,
            help='Use Playwright for JS rendering'
        )
        parser.add_argument(
            '--screenshot',
            action='store_true',
            default=True,
            help='Capture full-page screenshot'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            default=False,
            help='Force re-scraping even if recently scraped'
        )

    def handle(self, *args, **options):
        url = options['url']
        brand_id = options.get('brand_id')
        render_js = options['render_js']
        take_screenshot = options['screenshot']
        force = options['force']

        # Convert brand_id string to UUID if provided
        if brand_id:
            try:
                brand_id = uuid.UUID(brand_id)
            except ValueError:
                self.stderr.write(
                    self.style.ERROR(f'Invalid brand_id format: {brand_id}')
                )
                return

        self.stdout.write(
            self.style.SUCCESS(
                f'Starting store scraper for {url} '
                f'(JS: {render_js}, Screenshot: {take_screenshot})...'
            )
        )

        try:
            result = run_store_scrape(
                target_url=url,
                brand_id=brand_id,
                render_js=render_js,
                take_screenshot=take_screenshot,
                force=force
            )

            if result.get('success', True):
                self.stdout.write(
                    self.style.SUCCESS('Store scraping completed successfully')
                )
                self.stdout.write(f"Title: {result.get('title', 'N/A')}")
                self.stdout.write(f"Price: {result.get('price', 'N/A')} {result.get('currency', '')}")
                self.stdout.write(f"Images found: {len(result.get('images', []))}")
                if result.get('screenshot_url'):
                    self.stdout.write(f"Screenshot: {result['screenshot_url']}")
            else:
                self.stdout.write(
                    self.style.ERROR(f'Store scraping failed: {result.get("error", "Unknown error")}')
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Store scraping failed with exception: {e}')
            )
            raise
