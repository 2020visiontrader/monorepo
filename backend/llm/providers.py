"""
LLM provider abstraction
"""
from abc import ABC, abstractmethod
from django.conf import settings
from typing import Dict, List, Optional
from .base import LLMProvider
from .mock_provider import MockLLMProvider
# TODO: Add OpenAI, Anthropic providers when needed


class LLMProvider(ABC):
    """Abstract LLM provider interface"""
    
    @abstractmethod
    def generate_content(self, product_title: str, product_description: str, brand_tone: Dict, required_terms: List[str], forbidden_terms: List[str], variant_number: int) -> Dict:
        """Generate content variant"""
        pass
    
    @abstractmethod
    def generate_seo(self, brand_name: str, scope: str, items: List[Dict]) -> Dict:
        """Generate SEO optimization"""
        pass
    
    @abstractmethod
    def generate_blueprint(self, brand_profile: Dict, ia_signatures: List[Dict]) -> Dict:
        """Generate site blueprint"""
        pass
    
    @abstractmethod
    def generate_template(self, complexity: str, industry: str, brand_tone: Dict, competitor_refs: Optional[List[str]] = None) -> Dict:
        """Generate store template"""
        pass


def get_llm_provider() -> LLMProvider:
    """Get LLM provider based on settings"""
    if settings.LLM_USE_MOCK or settings.LLM_PROVIDER == 'mock':
        return MockLLMProvider()
    
    # TODO: Add OpenAI, Anthropic providers
    # elif settings.LLM_PROVIDER == 'openai':
    #     return OpenAIProvider(api_key=settings.LLM_API_KEY, model=settings.LLM_MODEL)
    
    return MockLLMProvider()  # Default to mock

