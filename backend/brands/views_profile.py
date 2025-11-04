"""
Brand profile views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Brand, BrandProfile
from core.permissions import IsBrandManager


@api_view(['GET', 'PUT'])
@permission_classes([IsBrandManager])
def brand_profile_view(request, brand_id):
    """Get or update brand profile"""
    try:
        brand = Brand.objects.get(id=brand_id, organization_id=getattr(request, 'org_id', None))
    except Brand.DoesNotExist:
        return Response(
            {'detail': 'Brand not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    profile, _ = BrandProfile.objects.get_or_create(brand=brand)
    
    if request.method == 'GET':
        from .serializers import BrandProfileSerializer
        serializer = BrandProfileSerializer(profile)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        from .serializers import BrandProfileSerializer
        from competitors.models import CompetitorProfile
        
        # Validate competitor URL uniqueness if provided
        competitor_urls = request.data.get('competitor_urls', [])
        if competitor_urls:
            for url in competitor_urls:
                existing = CompetitorProfile.objects.filter(
                    brand__organization_id=brand.organization_id,
                    url=url
                ).exclude(brand=brand).first()
                if existing:
                    return Response(
                        {'detail': f'Competitor URL {url} already exists for another brand in this organization'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        serializer = BrandProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
