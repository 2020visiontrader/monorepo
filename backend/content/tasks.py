"""
Content generation and publishing tasks
"""
from celery import shared_task
from django.conf import settings
from .models import ProductDraft, ContentVariant, PublishJob
from llm.providers import get_llm_provider
from llm.schemas import ContentVariantSchema


@shared_task
def generate_content_task(brand_id, product_ids, fields, max_variants=3):
    """Generate content variants for products"""
    max_variants = min(max_variants, settings.MAX_VARIANTS)
    
    provider = get_llm_provider()
    
    for product_id in product_ids:
        product_draft = ProductDraft.objects.get(id=product_id, brand_id=brand_id)
        
        # Get brand profile for context
        brand_profile = product_draft.brand.profile
        
        # Generate variants
        for variant_num in range(1, max_variants + 1):
            # Call LLM with schema
            result = provider.generate_content(
                product_title=product_draft.original_title,
                product_description=product_draft.original_description,
                brand_tone=brand_profile.tone_sliders,
                required_terms=brand_profile.required_terms,
                forbidden_terms=brand_profile.forbidden_terms,
                variant_number=variant_num,
            )
            
            # Validate with Pydantic
            validated = ContentVariantSchema(**result)
            
            # Create variant
            ContentVariant.objects.create(
                product_draft=product_draft,
                variant_number=variant_num,
                title=validated.title,
                bullets=validated.bullets,
                long_description=validated.long_description,
                is_valid=True,
            )
    
    return {'status': 'completed'}


@shared_task
def publish_to_shopify_task(job_id):
    """Publish content to Shopify"""
    job = PublishJob.objects.get(id=job_id)
    job.status = 'RUNNING'
    job.save()
    
    try:
        # Import shopify client
        from shopify.client import ShopifyClient
        
        brand = job.brand
        shopify_client = ShopifyClient(
            shop=brand.profile.shopify_store,
            access_token=brand.profile.shopify_access_token
        )
        
        # Publish based on scope
        if job.scope == 'product':
            # Publish accepted variants
            variants = ContentVariant.objects.filter(
                product_draft__brand=brand,
                is_accepted=True
            )
            
            for variant in variants:
                shopify_client.update_product(
                    product_id=variant.product_draft.shopify_product_id,
                    title=variant.title,
                    description=variant.long_description,
                    bullets=variant.bullets,
                )
                job.items_published += 1
        
        job.status = 'COMPLETED'
    except Exception as e:
        job.status = 'FAILED'
        job.error = str(e)
        job.items_failed += 1
    
    job.save()
    return {'status': job.status}

