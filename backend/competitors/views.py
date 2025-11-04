"""
Competitor views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from django.conf import settings
from .models import CompetitorProfile, CrawlRun, IASignature
from .serializers import CompetitorProfileSerializer, IASignatureSerializer
from core.permissions import IsBrandManager
from core.models import BackgroundJob, JobLog
from core.throttling import CompetitorRecrawlThrottle
from .tasks import crawl_competitor_task


class CompetitorProfileViewSet(viewsets.ModelViewSet):
    queryset = CompetitorProfile.objects.all()
    serializer_class = CompetitorProfileSerializer
    permission_classes = [IsBrandManager]

    def get_queryset(self):
        brand_id = self.request.brand_id
        if brand_id:
            return CompetitorProfile.objects.filter(brand_id=brand_id)
        return CompetitorProfile.objects.none()

    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest(self, request):
        """Ingest competitor URLs"""
        brand_id = request.brand_id
        if not brand_id:
            return Response({'error': 'Brand ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        urls = request.data.get('urls', [])
        primary_url = request.data.get('primary')
        notes_map = request.data.get('notes', {})
        
        competitors = []
        for url in urls:
            competitor, created = CompetitorProfile.objects.get_or_create(
                brand_id=brand_id,
                url=url,
                defaults={
                    'is_primary': url == primary_url,
                    'emulate_notes': notes_map.get(url, {}).get('emulate', ''),
                    'avoid_notes': notes_map.get(url, {}).get('avoid', ''),
                }
            )
            competitors.append(competitor)
            
            # Trigger crawl task
            crawl_competitor_task.delay(str(competitor.id))
        
        serializer = self.get_serializer(competitors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='insights')
    def insights(self, request):
        """Get competitor insights"""
        brand_id = request.brand_id
        if not brand_id:
            return Response({'error': 'Brand ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        competitors = CompetitorProfile.objects.filter(brand_id=brand_id)
        insights = []
        
        for competitor in competitors:
            latest_ia = IASignature.objects.filter(competitor=competitor).first()
            insights.append({
                'competitor_id': str(competitor.id),
                'url': competitor.url,
                'name': competitor.name,
                'ia_summary': {
                    'navigation': latest_ia.navigation if latest_ia else [],
                    'sections': latest_ia.sections if latest_ia else [],
                    'taxonomy': latest_ia.taxonomy if latest_ia else {},
                } if latest_ia else None,
            })
        
        return Response({'insights': insights})


@api_view(['POST'])
@permission_classes([IsBrandManager])
@throttle_classes([CompetitorRecrawlThrottle])
def competitor_recrawl_view(request, competitor_id):
    """Trigger competitor recrawl"""
    brand_id = getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'Brand ID required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        competitor = CompetitorProfile.objects.get(id=competitor_id, brand_id=brand_id)
    except CompetitorProfile.DoesNotExist:
        return Response(
            {'detail': 'Competitor not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    force = request.data.get('force', False)
    max_pages = request.data.get('max_pages')
    
    # Determine max pages (apply cap)
    from brands.models import BrandProfile
    brand_profile, _ = BrandProfile.objects.get_or_create(brand=competitor.brand)
    default_max = settings.MAX_COMPETITOR_PAGES_SINGLE_SKU if brand_profile.single_sku else settings.MAX_COMPETITOR_PAGES
    max_pages = min(max_pages or default_max, default_max)
    
    # Create crawl run
    crawl_run = CrawlRun.objects.create(
        competitor=competitor,
        status='PENDING'
    )
    
    # Create job
    job = BackgroundJob.objects.create(
        task_name='crawl_competitor_task',
        status='PENDING',
        brand_id=competitor.brand_id,
        organization_id=competitor.brand.organization_id,
    )
    
    # Create initial log
    JobLog.objects.create(
        job=job,
        step='crawl',
        level='INFO',
        message=f'Starting crawl for {competitor.url}',
        idx=0,
    )
    
    # Enqueue task
    task = crawl_competitor_task.delay(str(competitor.id))
    job.task_id = task.id
    job.save()
    
    return Response({
        'crawl_run_id': str(crawl_run.id),
        'job_id': str(job.id)
    }, status=status.HTTP_202_ACCEPTED)

