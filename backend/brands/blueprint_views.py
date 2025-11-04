"""
Blueprint generation views
"""
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Brand
from core.permissions import IsBrandManager
from llm.providers import get_llm_provider
from competitors.models import IASignature


@api_view(['POST'])
@permission_classes([IsBrandManager])
def generate_blueprint(request, brand_id):
    """Generate site blueprint"""
    try:
        brand = Brand.objects.get(id=brand_id)
    except Brand.DoesNotExist:
        return Response({'error': 'Brand not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Get brand profile
    brand_profile = brand.profile
    
    # Get IA signatures from competitors
    competitors = brand.competitors.all()
    ia_signatures = []
    for competitor in competitors:
        latest_ia = IASignature.objects.filter(competitor=competitor).first()
        if latest_ia:
            ia_signatures.append({
                'navigation': latest_ia.navigation,
                'sections': latest_ia.sections,
                'taxonomy': latest_ia.taxonomy,
            })
    
    # Generate blueprint
    provider = get_llm_provider()
    blueprint = provider.generate_blueprint(
        brand_profile={
            'mission': brand_profile.mission,
            'categories': brand_profile.categories,
            'tone_sliders': brand_profile.tone_sliders,
        },
        ia_signatures=ia_signatures
    )
    
    return Response(blueprint)

