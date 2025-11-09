"""
Content views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes, throttle_classes
from core.throttling import ContentGenerateThrottle
from rest_framework.response import Response
from django.conf import settings
from .models import ProductDraft, ContentVariant, PublishJob
from .serializers import ProductDraftSerializer, ContentVariantSerializer, PublishJobSerializer
from core.permissions import IsEditorOrAbove
from core.models import BackgroundJob, JobLog
from .tasks import generate_content_task, publish_to_shopify_task


class ProductDraftViewSet(viewsets.ModelViewSet):
    queryset = ProductDraft.objects.all()
    serializer_class = ProductDraftSerializer
    permission_classes = [IsEditorOrAbove]

    def get_queryset(self):
        brand_id = self.request.brand_id
        if brand_id:
            return ProductDraft.objects.filter(brand_id=brand_id)
        return ProductDraft.objects.none()


class ContentVariantViewSet(viewsets.ModelViewSet):
    queryset = ContentVariant.objects.all()
    serializer_class = ContentVariantSerializer
    permission_classes = [IsEditorOrAbove]

    def get_queryset(self):
        brand_id = self.request.brand_id
        if brand_id:
            return ContentVariant.objects.filter(product_draft__brand_id=brand_id)
        return ContentVariant.objects.none()

    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        """Accept a variant"""
        variant = self.get_object()
        variant.is_accepted = True
        variant.is_rejected = False
        variant.save()
        return Response({'status': 'accepted'})

    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """Reject a variant"""
        variant = self.get_object()
        variant.is_accepted = False
        variant.is_rejected = True
        variant.save()
        return Response({'status': 'rejected'})


class PublishJobViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PublishJob.objects.all()
    serializer_class = PublishJobSerializer
    permission_classes = [IsEditorOrAbove]

    def get_queryset(self):
        brand_id = self.request.brand_id
        if brand_id:
            return PublishJob.objects.filter(brand_id=brand_id)
        return PublishJob.objects.none()

    @action(detail=False, methods=['post'], url_path='publish')
    def publish(self, request):
        """Publish content to Shopify"""
        brand_id = request.brand_id
        if not brand_id:
            return Response({'error': 'Brand ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        scope = request.data.get('scope')
        changeset_id = request.data.get('changeset_id')
        
        # Create publish job
        job = PublishJob.objects.create(
            brand_id=brand_id,
            scope=scope,
            changeset_id=changeset_id,
            status='PENDING'
        )
        
        # Trigger task
        publish_to_shopify_task.delay(str(job.id))
        
        return Response({
            'job_id': str(job.id),
            'status': 'pending'
        })


@api_view(['POST'])
@permission_classes([IsEditorOrAbove])
@throttle_classes([ContentGenerateThrottle])
def content_generate_view(request):
    """Generate content variants"""
    from core.models import IdempotencyKey
    from django.utils import timezone
    from datetime import timedelta
    import uuid as uuid_lib
    
    # Check idempotency key
    idem_key_str = request.headers.get('Idempotency-Key')
    if idem_key_str:
        try:
            idem_key = uuid_lib.UUID(idem_key_str)
            # Check for existing response
            existing = IdempotencyKey.objects.filter(
                key=idem_key,
                route='content_generate',
                user_id=request.user.id,
                brand_id=getattr(request, 'brand_id', None),
                created_at__gte=timezone.now() - timedelta(hours=24)
            ).first()
            if existing:
                return Response(
                    existing.response_data,
                    status=existing.response_status
                )
        except (ValueError, TypeError):
            pass  # Invalid UUID, continue normally
    
    brand_id = request.data.get('brand_id') or getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'Brand ID required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify RBAC + brand ownership
    try:
        from brands.models import Brand
        brand = Brand.objects.get(id=brand_id, organization_id=getattr(request, 'org_id', None))
    except Brand.DoesNotExist:
        return Response(
            {'detail': 'Brand not found or access denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    product_ids = request.data.get('product_ids', [])
    fields = request.data.get('fields', [])
    max_variants = request.data.get('variants', 3)
    
    # Validate
    if not product_ids:
        return Response(
            {'detail': 'product_ids required'},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    if not fields:
        return Response(
            {'detail': 'fields required'},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY
        )
    
    valid_fields = {'title', 'bullets', 'description'}
    if not all(f in valid_fields for f in fields):
        return Response(
            {'detail': f'Invalid fields. Must be one of: {valid_fields}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if max_variants > settings.MAX_VARIANTS:
        return Response(
            {'detail': f'variants must be <= {settings.MAX_VARIANTS}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Verify products belong to brand
    products = ProductDraft.objects.filter(id__in=product_ids, brand_id=brand_id)
    if products.count() != len(product_ids):
        return Response(
            {'detail': 'Some products not found or do not belong to brand'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Create job
    job = BackgroundJob.objects.create(
        task_name='generate_content_task',
        status='PENDING',
        brand_id=brand_id,
        organization_id=brand.organization_id,
    )
    
    # Create initial log
    JobLog.objects.create(
        job=job,
        step='validation',
        level='INFO',
        message='Content generation started',
        idx=0,
    )
    
    # Enqueue task
    task = generate_content_task.delay(
        brand_id=brand_id,
        product_ids=[str(pid) for pid in product_ids],
        fields=fields,
        max_variants=max_variants
    )
    job.task_id = task.id
    job.save()
    
    response_data = {
        'job_id': str(job.id)
    }
    response_status = status.HTTP_202_ACCEPTED
    
    # AI Framework Integration (guarded, additive)
    from ai.services.framework_flags import is_framework_enabled, is_framework_shadow
    
    if is_framework_enabled('product_copy'):
        try:
            # Import only when feature is enabled
            from ai.models import FrameworkRun
            from ai.tasks import shadow_run_product_copy
            
            input_data = {
                'product_ids': product_ids,
                'fields': fields,
                'max_variants': max_variants,
                'brand_id': str(brand_id),
            }
            input_hash = FrameworkRun.hash_input(input_data)
            baseline_output = {'job_id': str(job.id)}  # Current response
            
            if is_framework_shadow('product_copy'):
                # Shadow mode: run in background, don't affect response
                shadow_run_product_copy.delay(
                    product_ids=[str(p) for p in product_ids],
                    fields=fields,
                    brand_id=str(brand_id),
                    max_variants=max_variants,
                    baseline_output=baseline_output,
                    input_hash=input_hash,
                )
            else:
                # Active mode: try framework, fallback to baseline on error
                try:
                    from ai.frameworks.product_copy import generate_product_copy
                    ai_output = generate_product_copy(
                        product_ids=[str(p) for p in product_ids],
                        fields=fields,
                        brand_id=str(brand_id),
                        max_variants=max_variants,
                    )
                    # Map AI output to existing response shape (keep job_id)
                    # For now, keep existing response to avoid breaking changes
                    logger.info(f"AI framework generated content for brand {brand_id}")
                except Exception as e:
                    logger.warning(f"AI framework failed, using baseline: {e}")
                    # Fallback to existing response
        except Exception as e:
            logger.warning(f"AI framework integration error (non-blocking): {e}")
    
    # Store idempotency key if provided
    if idem_key_str:
        try:
            idem_key = uuid_lib.UUID(idem_key_str)
            IdempotencyKey.objects.create(
                key=idem_key,
                route='content_generate',
                user_id=request.user.id,
                brand_id=brand_id,
                response_status=response_status,
                response_data=response_data,
            )
        except (ValueError, TypeError):
            pass
    
    return Response(response_data, status=response_status)


@api_view(['POST'])
@permission_classes([IsEditorOrAbove])
def variants_bulk_accept_view(request):
    """Bulk accept content variants"""
    variant_ids = request.data.get('ids', [])
    if not variant_ids:
        return Response(
            {'detail': 'ids required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    brand_id = getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'Brand ID required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    variants = ContentVariant.objects.filter(
        id__in=variant_ids,
        product_draft__brand_id=brand_id
    )
    
    accepted = []
    failed = []
    
    for variant_id in variant_ids:
        try:
            variant = variants.get(id=variant_id)
            variant.is_accepted = True
            variant.is_rejected = False
            variant.save()
            accepted.append(str(variant_id))
        except ContentVariant.DoesNotExist:
            failed.append({
                'id': str(variant_id),
                'reason': 'Not found or access denied'
            })
        except Exception as e:
            failed.append({
                'id': str(variant_id),
                'reason': str(e)
            })
    
    return Response({
        'accepted': accepted,
        'failed': failed
    })


@api_view(['POST'])
@permission_classes([IsEditorOrAbove])
def variants_bulk_reject_view(request):
    """Bulk reject content variants"""
    variant_ids = request.data.get('ids', [])
    if not variant_ids:
        return Response(
            {'detail': 'ids required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    brand_id = getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'Brand ID required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    variants = ContentVariant.objects.filter(
        id__in=variant_ids,
        product_draft__brand_id=brand_id
    )
    
    rejected = []
    failed = []
    
    for variant_id in variant_ids:
        try:
            variant = variants.get(id=variant_id)
            variant.is_accepted = False
            variant.is_rejected = True
            variant.save()
            rejected.append(str(variant_id))
        except ContentVariant.DoesNotExist:
            failed.append({
                'id': str(variant_id),
                'reason': 'Not found or access denied'
            })
        except Exception as e:
            failed.append({
                'id': str(variant_id),
                'reason': str(e)
            })
    
    return Response({
        'rejected': rejected,
        'failed': failed
    })

