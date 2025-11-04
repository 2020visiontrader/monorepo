"""
Blueprint management views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
import logging
from .models import Brand
try:
    from .models import Blueprint
except ImportError:
    Blueprint = None
from core.permissions import IsBrandManager

logger = logging.getLogger(__name__)


@api_view(['GET', 'PUT'])
@permission_classes([IsBrandManager])
def blueprint_view(request, brand_id):
    """Get or update blueprint"""
    try:
        brand = Brand.objects.get(id=brand_id, organization_id=getattr(request, 'org_id', None))
    except Brand.DoesNotExist:
        return Response(
            {'detail': 'Brand not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        if Blueprint:
            blueprint = Blueprint.objects.filter(brand=brand).first()
            if blueprint:
                return Response({
                    'version': blueprint.version,
                    'json': blueprint.json
                })
        return Response({
            'version': 0,
            'json': {}
        })
    
    elif request.method == 'PUT':
        if not Blueprint:
            return Response(
                {'detail': 'Blueprint model not available'},
                status=status.HTTP_501_NOT_IMPLEMENTED
            )
        
        new_json = request.data.get('json', {})
        
        # Get current version
        current = Blueprint.objects.filter(brand=brand).first()
        new_version = (current.version + 1) if current else 1
        
        blueprint = Blueprint.objects.create(
            brand=brand,
            version=new_version,
            json=new_json,
            created_by=request.user,
        )
        
        response_data = {
            'version': blueprint.version,
            'json': blueprint.json
        }
        
        # AI Framework Integration (guarded, additive)
        from ai.services.framework_flags import is_framework_enabled, is_framework_shadow
        
        if is_framework_enabled('blueprint'):
            try:
                from ai.models import FrameworkRun
                from ai.tasks import shadow_run_blueprint
                
                input_data = {'requirements': new_json, 'brand_id': str(brand_id)}
                input_hash = FrameworkRun.hash_input(input_data)
                baseline_output = response_data.copy()
                
                if is_framework_shadow('blueprint'):
                    # Shadow mode: run in background
                    shadow_run_blueprint.delay(
                        requirements=new_json,
                        brand_id=str(brand_id),
                        baseline_output=baseline_output,
                        input_hash=input_hash,
                    )
                else:
                    # Active mode: try framework, fallback on error
                    try:
                        from ai.frameworks.blueprint import generate_blueprint
                        ai_output = generate_blueprint(new_json, str(brand_id))
                        # For now, keep existing response to avoid breaking changes
                        logger.info(f"AI framework generated blueprint for brand {brand_id}")
                    except Exception as e:
                        logger.warning(f"AI framework failed, using baseline: {e}")
            except Exception as e:
                logger.warning(f"AI framework integration error (non-blocking): {e}")
        
        return Response(response_data)


@api_view(['POST'])
@permission_classes([IsBrandManager])
def blueprint_sections_view(request, brand_id):
    """Mutate blueprint sections"""
    try:
        brand = Brand.objects.get(id=brand_id, organization_id=getattr(request, 'org_id', None))
    except Brand.DoesNotExist:
        return Response(
            {'detail': 'Brand not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    action_type = request.data.get('action')  # enable, disable, add, remove
    section_key = request.data.get('section_key')
    index = request.data.get('index')
    props = request.data.get('props', {})
    
    if not action_type or not section_key:
        return Response(
            {'detail': 'action and section_key required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get current blueprint
    if Blueprint:
        current = Blueprint.objects.filter(brand=brand).first()
        current_json = current.json if current else {}
    else:
        current_json = {}
    sections = current_json.get('sections', [])
    
    # Mutate sections
    if action_type == 'enable':
        for section in sections:
            if section.get('key') == section_key:
                section['enabled'] = True
    elif action_type == 'disable':
        for section in sections:
            if section.get('key') == section_key:
                section['enabled'] = False
    elif action_type == 'add':
        new_section = {'key': section_key, 'enabled': True, **props}
        if index is not None:
            sections.insert(index, new_section)
        else:
            sections.append(new_section)
    elif action_type == 'remove':
        sections = [s for s in sections if s.get('key') != section_key]
    
    # Update blueprint JSON
    current_json['sections'] = sections
    
    if not Blueprint:
        return Response(
            {'detail': 'Blueprint model not available'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    # Create new version
    current = Blueprint.objects.filter(brand=brand).first() if Blueprint else None
    new_version = (current.version + 1) if current else 1
    blueprint = Blueprint.objects.create(
        brand=brand,
        version=new_version,
        json=current_json,
        created_by=request.user,
    )
    
    return Response({
        'version': blueprint.version,
        'json': blueprint.json
    })

