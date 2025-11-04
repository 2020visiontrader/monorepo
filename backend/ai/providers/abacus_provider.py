"""
Abacus AI provider implementation
"""
from typing import Dict, Any
from django.conf import settings
from .base import AIProvider
import logging

logger = logging.getLogger(__name__)

# Track if we've logged the mock mode warning
_mock_warning_logged = False


class AbacusProvider(AIProvider):
    """Abacus-backed AI provider"""
    
    def __init__(self):
        self.api_key = getattr(settings, 'ROUTELLM_API_KEY', '') or getattr(settings, 'ABACUS_API_KEY', '')
        self.base_url = getattr(settings, 'ABACUS_BASE_URL', 'https://api.abacus.ai')
        
        # Hard safety: Force mock mode if no API key
        if not self.api_key or self.api_key.strip() == '':
            self.use_mock = True
            global _mock_warning_logged
            if not _mock_warning_logged:
                logger.warning("AbacusProvider in MOCK mode (no API key).")
                _mock_warning_logged = True
        else:
            # Check global mock setting
            self.use_mock = getattr(settings, 'LLM_USE_MOCK', True)
    
    def generate_content(self, prompt: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate content using Abacus"""
        # Hard safety: Never make network calls if in mock mode
        if self.use_mock or not self.api_key:
            logger.debug("AbacusProvider: Using mock content generation")
            return {
                'title': context.get('original_title', '') + ' (AI Enhanced)',
                'description': context.get('original_description', '') + ' [AI optimized]',
                'bullets': context.get('original_bullets', []) + ['AI-generated benefit'],
            }
        
        # TODO: Implement actual Abacus API call with httpx/requests
        # For now, if not in mock mode but no real implementation, log error
        logger.error("AbacusProvider: Real API not implemented but mock disabled. This should not happen.")
        raise RuntimeError("AbacusProvider: Real API implementation required when not in mock mode")
    
    def generate_seo(self, page_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO optimization using Abacus"""
        if self.use_mock or not self.api_key:
            logger.debug("AbacusProvider: Using mock SEO generation")
            return {
                'title': page_data.get('title', '') + ' | SEO Optimized',
                'meta_description': page_data.get('description', '')[:155] + '...',
                'h1': page_data.get('h1', ''),
                'keywords': context.get('keywords', []),
            }
        
        logger.error("AbacusProvider: Real API not implemented but mock disabled. This should not happen.")
        raise RuntimeError("AbacusProvider: Real API implementation required when not in mock mode")
    
    def generate_blueprint(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate site blueprint using Abacus"""
        if self.use_mock or not self.api_key:
            logger.debug("AbacusProvider: Using mock blueprint generation")
            return {
                'sections': [
                    {'key': 'hero', 'enabled': True, 'type': 'hero'},
                    {'key': 'features', 'enabled': True, 'type': 'features'},
                ],
                'theme_tokens': {
                    'primary': '#000000',
                    'secondary': '#666666',
                },
            }
        
        logger.error("AbacusProvider: Real API not implemented but mock disabled. This should not happen.")
        raise RuntimeError("AbacusProvider: Real API implementation required when not in mock mode")
    
    def analyze_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze changes between two states"""
        if self.use_mock or not self.api_key:
            logger.debug("AbacusProvider: Using mock change analysis")
            return {
                'summary': 'Changes detected',
                'fields_changed': list(set(before.keys()) ^ set(after.keys())),
                'confidence': 0.85,
            }
        
        logger.error("AbacusProvider: Real API not implemented but mock disabled. This should not happen.")
        raise RuntimeError("AbacusProvider: Real API implementation required when not in mock mode")


def get_ai_provider() -> AIProvider:
    """Get AI provider instance based on settings"""
    provider_name = getattr(settings, 'AI_PROVIDER', 'abacus')
    
    if provider_name == 'abacus':
        return AbacusProvider()
    else:
        raise ValueError(f"Unknown AI provider: {provider_name}")

