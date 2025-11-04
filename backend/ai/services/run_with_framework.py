"""
Run framework with caching and telemetry
"""
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any, Callable, Optional
from ai.models import FrameworkRun
from ai.services.framework_flags import get_framework_flag
import logging
import time
import hashlib
import json

logger = logging.getLogger(__name__)


def compute_input_hash(
    brand_id: str,
    framework_name: str,
    payload: Dict[str, Any],
    policy_version: Optional[str] = None,
) -> str:
    """
    Compute hash for input caching
    Includes brand_id, framework_name, payload, and policy_version
    """
    if policy_version is None:
        policy_version = getattr(settings, 'AI_POLICY_VERSION', '1.0')
    
    hash_input = {
        'brand_id': brand_id,
        'framework_name': framework_name,
        'payload': payload,
        'policy_version': policy_version,
    }
    
    json_str = json.dumps(hash_input, sort_keys=True)
    return hashlib.sha256(json_str.encode()).hexdigest()


def get_cached_output(input_hash: str, ttl_days: int = 7) -> Optional[Dict[str, Any]]:
    """
    Get cached framework output if available and not expired
    """
    cache_ttl = timedelta(days=ttl_days)
    cutoff = timezone.now() - cache_ttl
    
    # Look for recent successful run with same input_hash
    cached_run = FrameworkRun.objects.filter(
        input_hash=input_hash,
        status='SUCCESS',
        created_at__gte=cutoff,
        cached=False,  # Original run (not a cache lookup)
    ).order_by('-created_at').first()
    
    if cached_run and cached_run.output_data:
        logger.info(f"Cache hit for input_hash: {input_hash[:16]}...")
        return cached_run.output_data
    
    return None


def run_with_framework(
    framework_name: str,
    brand_id: str,
    payload: Dict[str, Any],
    framework_func: Callable,
    baseline_output: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Run framework with caching, telemetry, and per-framework flags
    
    Returns:
        {
            'output': {...},  # Framework output
            'cached': bool,
            'used_mock': bool,
            'model_name': str,
            'duration_ms': int,
            'framework_run_id': str,
        }
    """
    # Check if framework is enabled
    frameworks_enabled = get_framework_flag(framework_name, 'AI_FRAMEWORKS_ENABLED')
    if not frameworks_enabled:
        logger.debug(f"Framework {framework_name} disabled")
        return {
            'output': None,
            'cached': False,
            'used_mock': False,
            'model_name': None,
            'duration_ms': 0,
            'framework_run_id': None,
        }
    
    # Compute input hash
    input_hash = compute_input_hash(brand_id, framework_name, payload)
    
    # Check cache
    cache_ttl = getattr(settings, 'AI_CACHE_TTL_DAYS', 7)
    cached_output = get_cached_output(input_hash, cache_ttl)
    
    if cached_output:
        # Create FrameworkRun record for cache hit
        framework_run = FrameworkRun.objects.create(
            brand_id=brand_id,
            framework_name=framework_name,
            input_hash=input_hash,
            input_data=payload,
            output_data=cached_output,
            baseline_output=baseline_output,
            status='SUCCESS',
            is_shadow=get_framework_flag(framework_name, 'AI_SHADOW_MODE'),
            cached=True,  # Mark as cache hit
            duration_ms=0,  # No actual execution
            used_mock=True,  # Cache implies previous mock/real run
            model_tier='cached',
            model_name='cached',
            started_at=timezone.now(),
            completed_at=timezone.now(),
        )
        
        return {
            'output': cached_output,
            'cached': True,
            'used_mock': True,
            'model_name': 'cached',
            'duration_ms': 0,
            'framework_run_id': str(framework_run.id),
        }
    
    # Run framework
    shadow_mode = get_framework_flag(framework_name, 'AI_SHADOW_MODE')
    use_mock = get_framework_flag(framework_name, 'AI_USE_MOCK')
    
    # Hard safety: Force mock if no API key
    api_key = getattr(settings, 'ROUTELLM_API_KEY', '') or getattr(settings, 'ABACUS_API_KEY', '')
    if not api_key or api_key.strip() == '':
        use_mock = True
    
    # Create FrameworkRun record
    framework_run = FrameworkRun.objects.create(
        brand_id=brand_id,
        framework_name=framework_name,
        input_hash=input_hash,
        input_data=payload,
        baseline_output=baseline_output,
        status='RUNNING',
        is_shadow=shadow_mode,
        cached=False,
        used_mock=use_mock,
        started_at=timezone.now(),
    )
    
    start_time = time.time()
    
    try:
        # Run framework function
        output = framework_func()
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Get model info from provider
        model_name = 'mock' if use_mock else getattr(settings, 'AI_PROVIDER', 'abacus')
        model_tier = 'mock' if use_mock else 'standard'
        
        # Update FrameworkRun
        framework_run.output_data = output
        framework_run.status = 'SUCCESS'
        framework_run.completed_at = timezone.now()
        framework_run.duration_ms = duration_ms
        framework_run.model_name = model_name
        framework_run.model_tier = model_tier
        framework_run.save()
        
        logger.info(f"Framework {framework_name} completed: {duration_ms}ms, cached={False}, mock={use_mock}")
        
        return {
            'output': output,
            'cached': False,
            'used_mock': use_mock,
            'model_name': model_name,
            'duration_ms': duration_ms,
            'framework_run_id': str(framework_run.id),
        }
        
    except Exception as e:
        duration_ms = int((time.time() - start_time) * 1000)
        framework_run.status = 'FAILED'
        framework_run.error_message = str(e)
        framework_run.completed_at = timezone.now()
        framework_run.duration_ms = duration_ms
        framework_run.save()
        
        logger.error(f"Framework {framework_name} failed: {e}", exc_info=True)
        raise

