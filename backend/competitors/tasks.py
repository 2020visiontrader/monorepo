"""
Competitor crawl tasks
"""
from celery import shared_task
from .models import CompetitorProfile, CrawlRun, IASignature, PageNode
from .parsers import parse_competitor_site
from django.conf import settings


@shared_task
def crawl_competitor_task(competitor_id):
    """Crawl competitor website"""
    competitor = CompetitorProfile.objects.get(id=competitor_id)
    
    crawl_run = CrawlRun.objects.create(
        competitor=competitor,
        status='RUNNING'
    )
    
    try:
        # Determine max pages based on brand profile
        brand_profile = competitor.brand.profile
        max_pages = settings.MAX_COMPETITOR_PAGES_SINGLE_SKU if brand_profile.single_sku else settings.MAX_COMPETITOR_PAGES
        
        # Parse competitor site
        ia_data, pages = parse_competitor_site(competitor.url, max_pages=max_pages)
        
        # Create IA signature
        ia_signature = IASignature.objects.create(
            competitor=competitor,
            crawl_run=crawl_run,
            navigation=ia_data.get('navigation', []),
            sections=ia_data.get('sections', []),
            taxonomy=ia_data.get('taxonomy', {}),
        )
        
        # Create page nodes
        for page_data in pages:
            PageNode.objects.create(
                competitor=competitor,
                crawl_run=crawl_run,
                url=page_data['url'],
                title=page_data.get('title', ''),
                page_type=page_data.get('page_type', ''),
                depth=page_data.get('depth', 0),
                raw_html=page_data.get('raw_html', ''),
                extracted_text=page_data.get('extracted_text', ''),
                metadata=page_data.get('metadata', {}),
            )
        
        crawl_run.status = 'COMPLETED'
        crawl_run.pages_crawled = len(pages)
        crawl_run.completed_at = crawl_run.started_at
        
    except Exception as e:
        crawl_run.status = 'FAILED'
        crawl_run.error = str(e)
    
    crawl_run.save()
    return str(crawl_run.id)

