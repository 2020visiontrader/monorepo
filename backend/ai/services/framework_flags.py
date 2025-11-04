"""
Helper to resolve per-framework flags with fallback to global flags
"""
from django.conf import settings
from typing import Any, Optional


def get_framework_flag(framework_name: str, flag_name: str) -> Any:
    """
    Get framework-specific flag with fallback to global flag
    
    Args:
        framework_name: 'product_copy', 'seo', 'blueprint'
        flag_name: 'AI_FRAMEWORKS_ENABLED', 'AI_SHADOW_MODE', 'AI_USE_MOCK'
    
    Returns:
        Framework-specific value if set, otherwise global value
    """
    # Map flag names to per-framework dict settings
    flag_map = {
        'AI_FRAMEWORKS_ENABLED': 'AI_FRAMEWORKS_ENABLED_BY_NAME',
        'AI_SHADOW_MODE': 'AI_SHADOW_MODE_BY_NAME',
        'AI_USE_MOCK': 'AI_USE_MOCK_BY_FRAMEWORK',
    }
    
    per_framework_setting = flag_map.get(flag_name)
    
    # Check per-framework flag first
    if per_framework_setting:
        per_framework_dict = getattr(settings, per_framework_setting, {})
        if isinstance(per_framework_dict, dict) and framework_name in per_framework_dict:
            return per_framework_dict[framework_name]
    
    # Fallback to global flag
    if flag_name == 'AI_USE_MOCK':
        # Special handling: derive from LLM_USE_MOCK if global not set
        global_flag = getattr(settings, 'AI_USE_MOCK', None)
        if global_flag is None:
            return getattr(settings, 'LLM_USE_MOCK', True)
        return global_flag
    else:
        return getattr(settings, flag_name)


def is_framework_enabled(framework_name: str) -> bool:
    """Check if framework is enabled"""
    return get_framework_flag(framework_name, 'AI_FRAMEWORKS_ENABLED')


def is_framework_shadow(framework_name: str) -> bool:
    """Check if framework is in shadow mode"""
    return get_framework_flag(framework_name, 'AI_SHADOW_MODE')


def should_use_mock(framework_name: str) -> bool:
    """Check if framework should use mock"""
    return get_framework_flag(framework_name, 'AI_USE_MOCK')

