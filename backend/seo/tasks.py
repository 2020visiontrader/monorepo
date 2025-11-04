"""
SEO generation tasks
"""
from celery import shared_task
from .models import SEOPlan
from llm.providers import get_llm_provider
from llm.schemas import SEOProposalSchema


@shared_task
def generate_seo_task(brand_id, scope, items):
    """Generate SEO optimization"""
    provider = get_llm_provider()
    
    # Get or create SEO plan
    from brands.models import Brand
    brand = Brand.objects.get(id=brand_id)
    plan, created = SEOPlan.objects.get_or_create(brand=brand)
    
    # Generate SEO data
    result = provider.generate_seo(
        brand_name=brand.name,
        scope=scope,
        items=items,
    )
    
    # Validate with Pydantic
    validated = SEOProposalSchema(**result)
    
    # Update plan
    plan.titles = validated.titles
    plan.meta_descriptions = validated.meta_descriptions
    plan.h1_tags = validated.h1_tags
    plan.h2_tags = validated.h2_tags
    plan.h3_tags = validated.h3_tags
    plan.alt_texts = validated.alt_texts
    plan.internal_links = validated.internal_links
    plan.json_ld = validated.json_ld
    plan.save()
    
    return {'plan_id': str(plan.id), 'status': 'completed'}

