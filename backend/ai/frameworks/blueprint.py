"""
Site blueprint generation framework
Matches existing response shapes
"""
from typing import Dict, Any
from ai.providers.abacus_provider import get_ai_provider
from ai.services.brand_context import get_brand_context
import logging

logger = logging.getLogger(__name__)


def generate_blueprint(
    requirements: Dict[str, Any],
    brand_id: str,
) -> Dict[str, Any]:
    """
    Generate site blueprint using AI framework
    Returns shape matching existing Blueprint structure
    """
    try:
        from ai.services.framework_flags import should_use_mock
        use_mock = should_use_mock('blueprint')
        
        # Hard safety: Force mock if no API key
        from django.conf import settings
        api_key = getattr(settings, 'ROUTELLM_API_KEY', '') or getattr(settings, 'ABACUS_API_KEY', '')
        if not api_key or api_key.strip() == '':
            use_mock = True
        
        provider = get_ai_provider(use_mock=use_mock)
        context = get_brand_context(brand_id)
        
        blueprint = provider.generate_blueprint(requirements, {
            'brand_context': context,
        })
        
        # Map to existing Blueprint JSON shape
        return {
            'sections': blueprint.get('sections', []),
            'theme_tokens': blueprint.get('theme_tokens', {}),
            'framework': 'ai_blueprint',
        }
    except Exception as e:
        logger.error(f"AI framework blueprint failed: {e}", exc_info=True)
        raise

