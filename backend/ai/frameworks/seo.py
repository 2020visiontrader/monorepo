"""
SEO optimization framework
Matches existing response shapes
"""
from typing import Dict, Any
from ai.providers.abacus_provider import get_ai_provider
from ai.services.brand_context import get_brand_context
import logging

logger = logging.getLogger(__name__)


def optimize_seo(
    page_data: Dict[str, Any],
    brand_id: str,
) -> Dict[str, Any]:
    """
    Optimize SEO using AI framework
    Returns shape matching existing SEO response structure
    """
    try:
        from ai.services.framework_flags import should_use_mock
        use_mock = should_use_mock('seo')
        
        # Hard safety: Force mock if no API key
        from django.conf import settings
        api_key = getattr(settings, 'ROUTELLM_API_KEY', '') or getattr(settings, 'ABACUS_API_KEY', '')
        if not api_key or api_key.strip() == '':
            use_mock = True
        
        provider = get_ai_provider(use_mock=use_mock)
        context = get_brand_context(brand_id)
        
        optimized = provider.generate_seo(page_data, {
            'brand_context': context,
            'keywords': page_data.get('keywords', []),
        })
        
        # Map to existing SEO response shape
        return {
            'title': optimized.get('title', ''),
            'meta_description': optimized.get('meta_description', ''),
            'h1': optimized.get('h1', ''),
            'h2': page_data.get('h2', []),
            'h3': page_data.get('h3', []),
            'keywords': optimized.get('keywords', []),
            'score': 85,  # Placeholder
            'framework': 'ai_seo',
        }
    except Exception as e:
        logger.error(f"AI framework seo failed: {e}", exc_info=True)
        raise

