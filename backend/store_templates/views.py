"""
Store Templates views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from .models import Template, TemplateVariant
from .serializers import TemplateSerializer, TemplateVariantSerializer
from core.permissions import IsBrandManager
from core.models import IdempotencyKey
from django.utils import timezone
from datetime import timedelta
import uuid as uuid_lib
from llm.providers import get_llm_provider


class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.filter(is_active=True)
    serializer_class = TemplateSerializer
    permission_classes = [IsEditorOrAbove]

    def get_queryset(self):
        # Filter by brand if specified
        brand_id = self.request.brand_id
        if brand_id:
            return Template.objects.filter(brand_id=brand_id, is_active=True)
        # Or show all templates
        return Template.objects.filter(is_active=True)

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """Generate template with AI"""
        complexity = request.data.get('complexity', 'Starter')
        industry = request.data.get('industry', '')
        brand_tone = request.data.get('brand_tone', {})
        competitor_refs = request.data.get('competitor_refs', [])
        
        provider = get_llm_provider()
        template_data = provider.generate_template(
            complexity=complexity,
            industry=industry,
            brand_tone=brand_tone,
            competitor_refs=competitor_refs
        )
        
        # Create template
        template = Template.objects.create(
            name=template_data['meta']['name'],
            description=template_data['meta']['description'],
            complexity=complexity,
            source='generated',
            manifest=template_data,
            industry_tags=template_data['meta'].get('tags', []),
        )
        
        serializer = self.get_serializer(template)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='upload')
    def upload(self, request):
        """Upload template from file"""
        # TODO: Handle file upload and validation
        manifest = request.data.get('manifest', {})
        
        # Validate manifest schema (simplified)
        if 'meta' not in manifest or 'theme_tokens' not in manifest:
            return Response(
                {'error': 'Invalid template manifest'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        template = Template.objects.create(
            name=manifest['meta'].get('name', 'Uploaded Template'),
            description=manifest['meta'].get('description', ''),
            complexity=manifest['meta'].get('complexity', 'Starter'),
            source='uploaded',
            manifest=manifest,
            industry_tags=manifest['meta'].get('tags', []),
        )
        
        serializer = self.get_serializer(template)
        return Response(serializer.data)


class TemplateVariantViewSet(viewsets.ModelViewSet):
    queryset = TemplateVariant.objects.all()
    serializer_class = TemplateVariantSerializer
    permission_classes = [IsEditorOrAbove]

    def get_queryset(self):
        brand_id = self.request.brand_id
        if brand_id:
            return TemplateVariant.objects.filter(brand_id=brand_id)
        return TemplateVariant.objects.none()


@api_view(['POST'])
@permission_classes([IsBrandManager])
def apply_template_variant_view(request, variant_id):
    """Apply template variant to Site Blueprint"""
    # Check idempotency key
    idem_key_str = request.headers.get('Idempotency-Key')
    if idem_key_str:
        try:
            idem_key = uuid_lib.UUID(idem_key_str)
            brand_id = getattr(request, 'brand_id', None)
            # Check for existing response
            existing = IdempotencyKey.objects.filter(
                key=idem_key,
                route=f'template_apply_{variant_id}',
                user_id=request.user.id,
                brand_id=brand_id,
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).first()
            if existing:
                return Response(
                    existing.response_data,
                    status=existing.response_status
                )
        except (ValueError, TypeError):
            pass  # Invalid UUID, continue normally
    
    brand_id = getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'Brand ID required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        variant = TemplateVariant.objects.get(id=variant_id, brand_id=brand_id)
    except TemplateVariant.DoesNotExist:
        return Response(
            {'detail': 'Variant not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Get current blueprint
    try:
        from brands.models import Blueprint
        current_blueprint = Blueprint.objects.filter(brand_id=brand_id).first()
    except ImportError:
        return Response(
            {'detail': 'Blueprint model not available'},
            status=status.HTTP_501_NOT_IMPLEMENTED
        )
    
    current_json = current_blueprint.json if current_blueprint else {}
    variant_json = variant.manifest  # Use manifest field (not manifest_json)
    
    # Merge tokens and sections only
    new_json = current_json.copy()
    if 'theme_tokens' in variant_json:
        new_json['theme_tokens'] = variant_json['theme_tokens']
    if 'sections' in variant_json:
        new_json['sections'] = variant_json['sections']
    
    # Calculate diff
    old_tokens = current_json.get('theme_tokens', {})
    old_sections = current_json.get('sections', [])
    new_tokens = variant_json.get('theme_tokens', {})
    new_sections = variant_json.get('sections', [])
    
    diff = {
        'tokens_changed': old_tokens != new_tokens,
        'sections_changed': old_sections != new_sections,
    }
    
    # Create new blueprint version
    new_version = (current_blueprint.version + 1) if current_blueprint else 1
    blueprint = Blueprint.objects.create(
        brand_id=brand_id,
        version=new_version,
        json=new_json,
        created_by=request.user,
    )
    
    response_data = {
        'blueprint_id': str(blueprint.id),
        'version': blueprint.version,
        'diff': diff
    }
    response_status = status.HTTP_200_OK
    
    # Store idempotency key if provided
    if idem_key_str:
        try:
            idem_key = uuid_lib.UUID(idem_key_str)
            IdempotencyKey.objects.create(
                key=idem_key,
                route=f'template_apply_{variant_id}',
                user_id=request.user.id,
                brand_id=brand_id,
                response_status=response_status,
                response_data=response_data,
            )
        except (ValueError, TypeError):
            pass
    
    return Response(response_data, status=response_status)

