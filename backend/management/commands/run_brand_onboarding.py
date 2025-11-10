"""
Django management command to run brand onboarding agent.
"""

from django.core.management.base import BaseCommand
from agents.brands_agent import process_brand_onboarding


class Command(BaseCommand):
    help = 'Run the brand onboarding agent to process pending brand onboardings'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Starting brand onboarding agent...')
        )

        try:
            process_brand_onboarding()
            self.stdout.write(
                self.style.SUCCESS('Brand onboarding agent completed successfully')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Brand onboarding agent failed: {e}')
            )
            raise
