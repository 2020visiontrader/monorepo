"""
Celery tasks for AI framework shadow mode runs
"""
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from ai.models import FrameworkRun
from ai.frameworks.product_copy import generate_product_copy
from ai.frameworks.seo import optimize_seo
from ai.frameworks.blueprint import generate_blueprint
from ai.services.run_with_framework import run_with_framework
from ai.services.framework_flags import get_framework_flag, is_framework_enabled
import logging
import time

logger = logging.getLogger(__name__)


@shared_task
def shadow_run_product_copy(
    product_ids: list,
    fields: list,
    brand_id: str,
    max_variants: int,
    baseline_output: dict,
    input_hash: str,
):
    """Run product copy framework in shadow mode"""
    if not getattr(settings, 'AI_FRAMEWORKS_ENABLED', False):
        logger.warning("AI frameworks disabled, skipping shadow run")
        return
    
    try:
        # Use run_with_framework for caching and telemetry
        payload = {
            'product_ids': product_ids,
            'fields': fields,
            'max_variants': max_variants,
        }
        
        result = run_with_framework(
            framework_name='product_copy',
            brand_id=brand_id,
            payload=payload,
            framework_func=lambda: generate_product_copy(product_ids, fields, brand_id, max_variants),
            baseline_output=baseline_output,
        )
        
        ai_output = result['output']
        framework_run_id = result['framework_run_id']
        
        if framework_run_id:
            framework_run = FrameworkRun.objects.get(id=framework_run_id)
            # Calculate diff
            diff_summary = _calculate_diff(baseline_output, ai_output)
            framework_run.diff_summary = diff_summary
            framework_run.save()
        
        logger.info(f"Shadow run product_copy completed: {framework_run_id}")
    except Exception as e:
        logger.error(f"Shadow run product_copy failed: {e}", exc_info=True)


@shared_task
def shadow_run_seo(
    page_data: dict,
    brand_id: str,
    baseline_output: dict,
    input_hash: str,
):
    """Run SEO framework in shadow mode"""
    if not is_framework_enabled('seo'):
        logger.warning("SEO framework disabled, skipping shadow run")
        return
    
    try:
        payload = {'page_data': page_data}
        
        result = run_with_framework(
            framework_name='seo',
            brand_id=brand_id,
            payload=payload,
            framework_func=lambda: optimize_seo(page_data, brand_id),
            baseline_output=baseline_output,
        )
        
        ai_output = result['output']
        framework_run_id = result['framework_run_id']
        
        if framework_run_id:
            framework_run = FrameworkRun.objects.get(id=framework_run_id)
            diff_summary = _calculate_diff(baseline_output, ai_output)
            framework_run.diff_summary = diff_summary
            framework_run.save()
        
        if framework_run_id:
            logger.info(f"Shadow run seo completed: {framework_run_id}")
    except Exception as e:
        logger.error(f"Shadow run seo failed: {e}", exc_info=True)


@shared_task
def shadow_run_blueprint(
    requirements: dict,
    brand_id: str,
    baseline_output: dict,
    input_hash: str,
):
    """Run blueprint framework in shadow mode"""
    if not is_framework_enabled('blueprint'):
        logger.warning("Blueprint framework disabled, skipping shadow run")
        return
    
    try:
        payload = {'requirements': requirements}
        
        result = run_with_framework(
            framework_name='blueprint',
            brand_id=brand_id,
            payload=payload,
            framework_func=lambda: generate_blueprint(requirements, brand_id),
            baseline_output=baseline_output,
        )
        
        ai_output = result['output']
        framework_run_id = result['framework_run_id']
        
        if framework_run_id:
            framework_run = FrameworkRun.objects.get(id=framework_run_id)
            diff_summary = _calculate_diff(baseline_output, ai_output)
            framework_run.diff_summary = diff_summary
            framework_run.save()
        
        if framework_run_id:
            logger.info(f"Shadow run blueprint completed: {framework_run_id}")
    except Exception as e:
        logger.error(f"Shadow run blueprint failed: {e}", exc_info=True)


def _calculate_diff(baseline: dict, ai_output: dict) -> dict:
    """Calculate diff between baseline and AI output"""
    keys_changed = []
    length_diff = {}
    
    for key in set(baseline.keys()) | set(ai_output.keys()):
        baseline_val = baseline.get(key)
        ai_val = ai_output.get(key)
        
        if baseline_val != ai_val:
            keys_changed.append(key)
            if isinstance(baseline_val, str) and isinstance(ai_val, str):
                length_diff[key] = len(ai_val) - len(baseline_val)
    
    # Lint results (basic validation)
    lint_results = {}
    if 'variants' in ai_output:
        from ai.validators import validate_content_variant
        lint_errors = []
        for variant in ai_output.get('variants', []):
            is_valid, errors = validate_content_variant(variant)
            if not is_valid:
                lint_errors.extend(errors)
        lint_results['validation_errors'] = lint_errors
        lint_results['passed'] = len(lint_errors) == 0
    
    return {
        'keys_changed': keys_changed,
        'length_diff': length_diff,
        'lint_results': lint_results,
    }

