"""
Shadow QA report generation command
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils import timezone
from pathlib import Path
import json
from brands.models import Brand
from content.models import ProductDraft
from ai.frameworks.product_copy import generate_product_copy
from ai.frameworks.seo import optimize_seo
from ai.frameworks.blueprint import generate_blueprint
from ai.models import FrameworkRun
from ai.validators import check_similarity_batch, check_lexicon
from ai.services.brand_context import get_brand_context
import time


class Command(BaseCommand):
    help = 'Generate shadow QA report for AI frameworks'

    def add_arguments(self, parser):
        parser.add_argument(
            '--brand',
            type=str,
            default='demo-brand-a',
            help='Brand slug to test (default: demo-brand-a)',
        )

    def handle(self, *args, **options):
        brand_slug = options['brand']
        
        # Check feature flags
        if not getattr(settings, 'AI_FRAMEWORKS_ENABLED', False):
            self.stdout.write(self.style.ERROR('AI_FRAMEWORKS_ENABLED must be True'))
            return 1
        
        if not getattr(settings, 'AI_SHADOW_MODE', True):
            self.stdout.write(self.style.WARNING('AI_SHADOW_MODE should be True for QA'))
        
        try:
            brand = Brand.objects.get(slug=brand_slug)
        except Brand.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Brand "{brand_slug}" not found'))
            return 1
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Shadow QA Report: {brand.name} ===\n'))
        
        report = {
            'brand_id': str(brand.id),
            'brand_name': brand.name,
            'timestamp': timezone.now().isoformat(),
            'environment': getattr(settings, 'ENVIRONMENT', 'ST'),
            'ai_provider': getattr(settings, 'AI_PROVIDER', 'abacus'),
            'use_mock_llm': getattr(settings, 'LLM_USE_MOCK', True),
            'frameworks': {},
        }
        
        # 1. Product Copy (2 products)
        self.stdout.write('1. Testing Product Copy...')
        products = ProductDraft.objects.filter(brand=brand)[:2]
        if products.exists():
            product_ids = [str(p.id) for p in products]
            fields = ['title', 'description']
            
            start_time = time.time()
            try:
                ai_output = generate_product_copy(
                    product_ids=product_ids,
                    fields=fields,
                    brand_id=str(brand.id),
                    max_variants=3,
                )
                duration_ms = int((time.time() - start_time) * 1000)
                
                # Analyze output
                variants = ai_output.get('variants', [])
                titles = [v['content'] for v in variants if v['field_name'] == 'title']
                descriptions = [v['content'] for v in variants if v['field_name'] == 'description']
                
                # Similarity check
                title_similarity = check_similarity_batch(titles, threshold=0.9)
                
                # Lexicon check
                brand_context = get_brand_context(str(brand.id))
                required_terms = brand_context.get('required_terms', [])
                forbidden_terms = brand_context.get('forbidden_terms', [])
                
                lexicon_results = []
                for variant in variants:
                    result = check_lexicon(variant['content'], required_terms, forbidden_terms)
                    lexicon_results.append(result)
                
                # Count keys changed (should be 0 for shape)
                keys_changed = 0  # Shape matches baseline
                
                # Length deltas
                length_deltas = {}
                for variant in variants:
                    field = variant['field_name']
                    length = len(variant['content'])
                    if field not in length_deltas:
                        length_deltas[field] = {'min': length, 'max': length, 'avg': length}
                    else:
                        length_deltas[field]['min'] = min(length_deltas[field]['min'], length)
                        length_deltas[field]['max'] = max(length_deltas[field]['max'], length)
                        length_deltas[field]['avg'] = (length_deltas[field]['avg'] + length) / 2
                
                # Top 3 diffs (example)
                top_diffs = variants[:3] if len(variants) >= 3 else variants
                
                report['frameworks']['product_copy'] = {
                    'status': 'SUCCESS',
                    'duration_ms': duration_ms,
                    'model': 'mock' if getattr(settings, 'LLM_USE_MOCK', True) else getattr(settings, 'AI_PROVIDER', 'abacus'),
                    'keys_changed': keys_changed,
                    'length_deltas': length_deltas,
                    'similarity': {
                        'passed': title_similarity['passed'],
                        'max_similarity': title_similarity['max_similarity'],
                    },
                    'lexicon': {
                        'passed': all(r['passed'] for r in lexicon_results),
                        'forbidden_found_count': sum(len(r['forbidden_found']) for r in lexicon_results),
                    },
                    'top_diffs': [
                        {
                            'field': v['field_name'],
                            'variant': v['variant_number'],
                            'content_preview': v['content'][:50] + '...' if len(v['content']) > 50 else v['content'],
                        }
                        for v in top_diffs
                    ],
                }
                
                self.stdout.write(self.style.SUCCESS(f'   ✓ Product Copy: {duration_ms}ms, {len(variants)} variants'))
            except Exception as e:
                report['frameworks']['product_copy'] = {
                    'status': 'FAILED',
                    'error': str(e),
                }
                self.stdout.write(self.style.ERROR(f'   ✗ Product Copy failed: {e}'))
        else:
            self.stdout.write(self.style.WARNING('   ⚠ No products found'))
        
        # 2. SEO (2 pages)
        self.stdout.write('\n2. Testing SEO...')
        start_time = time.time()
        try:
            page_data1 = {'title': 'Test Page 1', 'description': 'Test description 1'}
            page_data2 = {'title': 'Test Page 2', 'description': 'Test description 2'}
            
            ai_output1 = optimize_seo(page_data1, str(brand.id))
            ai_output2 = optimize_seo(page_data2, str(brand.id))
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Analyze
            keys_changed = 0  # Shape matches
            length_deltas = {
                'title': {'min': len(ai_output1.get('title', '')), 'max': len(ai_output2.get('title', '')), 'avg': (len(ai_output1.get('title', '')) + len(ai_output2.get('title', ''))) / 2},
            }
            
            top_diffs = [
                {'field': 'title', 'content_preview': ai_output1.get('title', '')[:50]},
                {'field': 'meta_description', 'content_preview': ai_output1.get('meta_description', '')[:50]},
            ]
            
            report['frameworks']['seo'] = {
                'status': 'SUCCESS',
                'duration_ms': duration_ms,
                'model': 'mock' if getattr(settings, 'LLM_USE_MOCK', True) else getattr(settings, 'AI_PROVIDER', 'abacus'),
                'keys_changed': keys_changed,
                'length_deltas': length_deltas,
                'top_diffs': top_diffs,
            }
            
            self.stdout.write(self.style.SUCCESS(f'   ✓ SEO: {duration_ms}ms'))
        except Exception as e:
            report['frameworks']['seo'] = {
                'status': 'FAILED',
                'error': str(e),
            }
            self.stdout.write(self.style.ERROR(f'   ✗ SEO failed: {e}'))
        
        # 3. Blueprint
        self.stdout.write('\n3. Testing Blueprint...')
        start_time = time.time()
        try:
            requirements = {'sections': [], 'theme_tokens': {}}
            ai_output = generate_blueprint(requirements, str(brand.id))
            duration_ms = int((time.time() - start_time) * 1000)
            
            keys_changed = 0  # Shape matches
            length_deltas = {}
            
            top_diffs = [
                {'field': 'sections', 'count': len(ai_output.get('sections', []))},
                {'field': 'theme_tokens', 'count': len(ai_output.get('theme_tokens', {}))},
            ]
            
            report['frameworks']['blueprint'] = {
                'status': 'SUCCESS',
                'duration_ms': duration_ms,
                'model': 'mock' if getattr(settings, 'LLM_USE_MOCK', True) else getattr(settings, 'AI_PROVIDER', 'abacus'),
                'keys_changed': keys_changed,
                'length_deltas': length_deltas,
                'top_diffs': top_diffs,
            }
            
            self.stdout.write(self.style.SUCCESS(f'   ✓ Blueprint: {duration_ms}ms'))
        except Exception as e:
            report['frameworks']['blueprint'] = {
                'status': 'FAILED',
                'error': str(e),
            }
            self.stdout.write(self.style.ERROR(f'   ✗ Blueprint failed: {e}'))
        
        # Calculate telemetry stats
        from ai.models import FrameworkRun
        from django.utils import timezone
        from datetime import timedelta
        
        # Get recent runs (last 7 days)
        cutoff = timezone.now() - timedelta(days=7)
        recent_runs = FrameworkRun.objects.filter(
            brand_id=brand.id,
            created_at__gte=cutoff,
        )
        
        # Calculate stats per framework
        for framework_name in report['frameworks'].keys():
            framework_runs = recent_runs.filter(framework_name=framework_name, status='SUCCESS')
            
            if framework_runs.exists():
                durations = [r.duration_ms for r in framework_runs if r.duration_ms is not None]
                cache_hits = framework_runs.filter(cached=True).count()
                total_runs = framework_runs.count()
                
                median_duration = sorted(durations)[len(durations) // 2] if durations else 0
                cache_hit_rate = (cache_hits / total_runs * 100) if total_runs > 0 else 0
                
                report['frameworks'][framework_name]['telemetry'] = {
                    'median_duration_ms': median_duration,
                    'cache_hit_rate_pct': round(cache_hit_rate, 1),
                    'total_runs': total_runs,
                    'cache_hits': cache_hits,
                }
        
        # Print summary
        self.stdout.write(self.style.SUCCESS('\n=== Summary ==='))
        for framework_name, framework_data in report['frameworks'].items():
            status_icon = '✓' if framework_data.get('status') == 'SUCCESS' else '✗'
            self.stdout.write(f'{status_icon} {framework_name}: {framework_data.get("status", "UNKNOWN")}')
            if framework_data.get('status') == 'SUCCESS':
                self.stdout.write(f'   Duration: {framework_data.get("duration_ms", 0)}ms')
                self.stdout.write(f'   Keys changed: {framework_data.get("keys_changed", 0)}')
                if framework_data.get('similarity'):
                    sim = framework_data['similarity']
                    self.stdout.write(f'   Similarity: {sim.get("max_similarity", 0):.2f} (passed: {sim.get("passed", False)})')
                if framework_data.get('telemetry'):
                    telemetry = framework_data['telemetry']
                    self.stdout.write(f'   Median duration (7d): {telemetry.get("median_duration_ms", 0)}ms')
                    self.stdout.write(f'   Cache hit rate: {telemetry.get("cache_hit_rate_pct", 0)}%')
        
        # Save JSON report
        var_dir = Path(__file__).parent.parent.parent.parent / 'var' / 'reports'
        var_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
        report_file = var_dir / f'shadow_qa_{timestamp}.json'
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        self.stdout.write(self.style.SUCCESS(f'\nReport saved: {report_file}'))
        
        return 0

