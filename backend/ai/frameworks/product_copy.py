"""
Product copy generation framework
Matches existing response shapes
"""
from typing import Dict, Any, List
from ai.providers.abacus_provider import get_ai_provider
from ai.services.brand_context import get_brand_context
import logging

logger = logging.getLogger(__name__)


def generate_product_copy(
    product_ids: List[str],
    fields: List[str],
    brand_id: str,
    max_variants: int = 3,
) -> Dict[str, Any]:
    """
    Generate product copy variants using AI framework
    Returns shape matching existing ContentVariant structure
    """
    try:
        from ai.services.framework_flags import should_use_mock
        use_mock = should_use_mock('product_copy')
        
        # Hard safety: Force mock if no API key
        from django.conf import settings
        api_key = getattr(settings, 'ROUTELLM_API_KEY', '') or getattr(settings, 'ABACUS_API_KEY', '')
        if not api_key or api_key.strip() == '':
            use_mock = True
        
        provider = get_ai_provider(use_mock=use_mock)
        context = get_brand_context(brand_id)
        
        results = []
        for product_id in product_ids:
            # TODO: Fetch product data from ProductDraft
            from content.models import ProductDraft
            try:
                product = ProductDraft.objects.get(id=product_id)
                product_data = {
                    'id': product_id,
                    'original_title': product.original_title,
                    'original_description': product.original_description,
                }
            except ProductDraft.DoesNotExist:
                product_data = {
                    'id': product_id,
                    'original_title': 'Product Title',
                    'original_description': 'Product Description',
                }
            
            for field in fields:
                for variant_num in range(1, max_variants + 1):
                    prompt = f"Generate {field} variant {variant_num} for product {product_id}"
                    generated = provider.generate_content(prompt, {
                        **product_data,
                        'brand_context': context,
                    })
                    
                    # Map to existing ContentVariant shape
                    variant = {
                        'product_id': product_id,
                        'field_name': field,
                        'variant_number': variant_num,
                        'content': generated.get(field, ''),
                        'is_valid': True,
                        'validation_errors': [],
                    }
                    results.append(variant)
        
        return {
            'variants': results,
            'framework': 'ai_product_copy',
        }
    except Exception as e:
        logger.error(f"AI framework product_copy failed: {e}", exc_info=True)
        raise

