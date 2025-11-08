"""
Onboarding helper functions for BrandProfile updates.
Handles syncing onboarding responses into permanent BrandProfile fields.
"""
from django.db import transaction
from django.utils import timezone


def sync_onboarding_responses(brand_profile, responses: dict) -> bool:
    """
    Sync onboarding responses into BrandProfile permanent fields.
    
    Args:
        brand_profile: BrandProfile instance to update
        responses: Dict with brand_identity and store_config data
        
    Returns:
        bool: True if sync successful
        
    The responses dict should follow this structure:
    {
        "brand_identity": {
            "mission": str,
            "tone": str,
            "categories": list,
            "personas": list,
            "values": list,
            ...
        },
        "store_config": {
            "platform": str,  # "shopify", "woocommerce", etc
            "store_url": str,
            "connected_at": datetime,
            ...
        }
    }
    """
    if not responses:
        return False
        
    try:
        with transaction.atomic():
            # Initialize JSON fields if null
            brand_profile.brand_identity = brand_profile.brand_identity or {}
            brand_profile.store_config = brand_profile.store_config or {}
            
            # Update brand identity (tone, mission, etc)
            if 'brand_identity' in responses:
                brand_identity = responses['brand_identity']
                brand_profile.brand_identity.update(brand_identity)
                
                # Legacy field support during transition
                if 'mission' in brand_identity:
                    brand_profile.mission = brand_identity['mission']
                if 'categories' in brand_identity:
                    brand_profile.categories = brand_identity['categories']
                if 'personas' in brand_identity:
                    brand_profile.personas = brand_identity['personas']
                if 'tone' in brand_identity:
                    brand_profile.tone_sliders = brand_identity.get('tone_sliders', {})
                    brand_profile.required_terms = brand_identity.get('required_terms', [])
                    brand_profile.forbidden_terms = brand_identity.get('forbidden_terms', [])
            
            # Update store config (platform, URL, credentials)
            if 'store_config' in responses:
                store_config = responses['store_config']
                brand_profile.store_config.update(store_config)
                
                # Legacy Shopify field support
                if store_config.get('platform') == 'shopify':
                    brand_profile.shopify_store = store_config.get('store_url', '')
                    brand_profile.shopify_access_token = store_config.get('access_token', '')
                    brand_profile.shopify_connected_at = store_config.get('connected_at', timezone.now())
            
            # Update last modified
            brand_profile.save(
                update_fields=[
                    'brand_identity', 'store_config',
                    'mission', 'categories', 'personas',
                    'tone_sliders', 'required_terms', 'forbidden_terms',
                    'shopify_store', 'shopify_access_token', 'shopify_connected_at'
                ]
            )
            
            return True
            
    except Exception:
        return False