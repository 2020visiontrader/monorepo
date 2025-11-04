"""
Brand context service for AI frameworks
"""
from typing import Dict, Any
from brands.models import Brand, BrandProfile
from competitors.models import CompetitorProfile
import logging

logger = logging.getLogger(__name__)


def get_brand_context(brand_id: str) -> Dict[str, Any]:
    """
    Get brand context for AI framework usage
    Includes profile, tone, competitors, etc.
    """
    try:
        brand = Brand.objects.get(id=brand_id)
        profile, _ = BrandProfile.objects.get_or_create(brand=brand)
        
        competitors = CompetitorProfile.objects.filter(brand=brand)
        
        return {
            'brand_id': str(brand.id),
            'brand_name': brand.name,
            'mission': profile.mission,
            'categories': profile.categories,
            'personas': profile.personas,
            'tone_sliders': profile.tone_sliders,
            'required_terms': profile.required_terms,
            'forbidden_terms': profile.forbidden_terms,
            'competitor_urls': [c.url for c in competitors],
            'single_sku': profile.single_sku,
        }
    except Brand.DoesNotExist:
        logger.warning(f"Brand {brand_id} not found for context")
        return {'brand_id': brand_id}
    except Exception as e:
        logger.error(f"Error getting brand context: {e}", exc_info=True)
        return {'brand_id': brand_id}

