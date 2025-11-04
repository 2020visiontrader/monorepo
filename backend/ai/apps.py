"""
AI app configuration
"""
from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AIConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai'
    verbose_name = 'AI Framework Integration'
    
    def ready(self):
        """Log AI framework status at startup"""
        # Import here to avoid circular imports
        from ai.services.framework_flags import (
            is_framework_enabled,
            is_framework_shadow,
            should_use_mock,
        )
        from ai.providers.abacus_provider import get_ai_provider
        
        frameworks = ['product_copy', 'seo', 'blueprint']
        ai_provider = getattr(settings, 'AI_PROVIDER', 'abacus')
        
        # Check API key status
        api_key = getattr(settings, 'ROUTELLM_API_KEY', '') or getattr(settings, 'ABACUS_API_KEY', '')
        has_api_key = bool(api_key and api_key.strip())
        
        logger.info("=" * 60)
        logger.info("AI Framework Status (Startup)")
        logger.info("=" * 60)
        logger.info(f"Provider: {ai_provider}")
        logger.info(f"API Key Present: {has_api_key}")
        if not has_api_key:
            logger.warning("  → MOCK mode enforced (no API key)")
        logger.info("-" * 60)
        
        for framework_name in frameworks:
            enabled = is_framework_enabled(framework_name)
            shadow = is_framework_shadow(framework_name)
            use_mock = should_use_mock(framework_name)
            
            # Hard safety: if no API key, mock is forced
            if not has_api_key:
                use_mock = True
            
            status_icon = "✓" if enabled else "✗"
            logger.info(
                f"{status_icon} [AI] Framework {framework_name}: "
                f"enabled={enabled}, shadow={shadow}, mock={use_mock}, provider={ai_provider}"
            )
        
        logger.info("=" * 60)

