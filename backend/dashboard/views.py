"""
Dashboard views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from core.permissions import IsEditorOrAbove
from core.models import BackgroundJob
from brands.models import Brand
from content.models import ProductDraft, ContentVariant
from competitors.models import CompetitorProfile
from django.utils import timezone
from datetime import timedelta


@api_view(['GET'])
@permission_classes([IsEditorOrAbove])
def dashboard_stats_view(request):
    """Get dashboard statistics"""
    brand_id = request.query_params.get('brand_id') or getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'brand_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        brand = Brand.objects.get(id=brand_id, organization_id=getattr(request, 'org_id', None))
    except Brand.DoesNotExist:
        return Response(
            {'detail': 'Brand not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Counts
    products_count = ProductDraft.objects.filter(brand=brand).count()
    variants_count = ContentVariant.objects.filter(product_draft__brand=brand).count()
    accepted_variants = ContentVariant.objects.filter(
        product_draft__brand=brand,
        is_accepted=True
    ).count()
    competitors_count = CompetitorProfile.objects.filter(brand=brand).count()
    
    # Recent jobs (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_jobs = BackgroundJob.objects.filter(
        brand_id=brand_id,
        created_at__gte=week_ago
    ).count()
    
    # Job status breakdown
    jobs_by_status = {}
    for status_choice in ['PENDING', 'STARTED', 'SUCCESS', 'FAILURE']:
        jobs_by_status[status_choice.lower()] = BackgroundJob.objects.filter(
            brand_id=brand_id,
            status=status_choice
        ).count()
    
    return Response({
        'brand_id': str(brand_id),
        'counts': {
            'products': products_count,
            'variants': variants_count,
            'accepted_variants': accepted_variants,
            'competitors': competitors_count,
            'recent_jobs': recent_jobs,
        },
        'jobs': jobs_by_status,
    })


@api_view(['GET'])
@permission_classes([IsEditorOrAbove])
def dashboard_activities_view(request):
    """Get recent dashboard activities"""
    brand_id = request.query_params.get('brand_id') or getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'brand_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        brand = Brand.objects.get(id=brand_id, organization_id=getattr(request, 'org_id', None))
    except Brand.DoesNotExist:
        return Response(
            {'detail': 'Brand not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Recent jobs (last 10)
    recent_jobs = BackgroundJob.objects.filter(
        brand_id=brand_id
    ).order_by('-created_at')[:10]
    
    activities = []
    for job in recent_jobs:
        activities.append({
            'id': str(job.id),
            'type': 'job',
            'task_name': job.task_name,
            'status': job.status.lower(),
            'created_at': job.created_at.isoformat(),
        })
    
    return Response({
        'brand_id': str(brand_id),
        'activities': activities,
    })

