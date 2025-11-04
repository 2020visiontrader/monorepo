"""
Shopify OAuth views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import redirect
from .models import ShopifyConnection
from .serializers import ShopifyConnectionSerializer
from core.permissions import IsBrandManager
from brands.models import BrandProfile
import secrets


class ShopifyOAuthViewSet(viewsets.ViewSet):
    """Shopify OAuth endpoints"""
    permission_classes = [IsBrandManager]
    
    @action(detail=False, methods=['get'], url_path='install')
    def install(self, request):
        """Initiate Shopify OAuth"""
        brand_id = request.brand_id
        if not brand_id:
            return Response({'error': 'Brand ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        shop = request.query_params.get('shop')
        if not shop:
            return Response({'error': 'Shop parameter required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate OAuth state
        state = secrets.token_urlsafe(32)
        
        # Store state (in production, use Redis or session)
        connection, created = ShopifyConnection.objects.get_or_create(
            brand_id=brand_id,
            defaults={'shop': shop, 'oauth_state': state}
        )
        if not created:
            connection.oauth_state = state
            connection.save()
        
        # Build OAuth URL
        scopes = 'read_products,write_products,read_content,write_content'
        redirect_uri = settings.SHOPIFY_REDIRECT_URI
        oauth_url = (
            f"https://{shop}/admin/oauth/authorize"
            f"?client_id={settings.SHOPIFY_API_KEY}"
            f"&scope={scopes}"
            f"&redirect_uri={redirect_uri}"
            f"&state={state}"
        )
        
        return Response({'oauth_url': oauth_url})
    
    @action(detail=False, methods=['get'], url_path='callback')
    def callback(self, request):
        """Handle Shopify OAuth callback"""
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        shop = request.query_params.get('shop')
        
        if not all([code, state, shop]):
            return Response({'error': 'Missing parameters'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verify state
        try:
            connection = ShopifyConnection.objects.get(oauth_state=state, shop=shop)
        except ShopifyConnection.DoesNotExist:
            return Response({'error': 'Invalid state'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Exchange code for access token
        # TODO: Implement actual OAuth token exchange
        # For now, store the code
        connection.oauth_code = code
        connection.save()
        
        # In production, exchange code for token via Shopify API
        # access_token = exchange_code_for_token(code, shop)
        # connection.access_token = access_token
        # connection.save()
        
        return Response({'status': 'connected', 'shop': shop})


@api_view(['GET'])
@permission_classes([IsBrandManager])
def connection_status_view(request):
    """Get Shopify connection status"""
    brand_id = request.query_params.get('brand_id') or getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'brand_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from brands.models import Brand, BrandProfile
        brand = Brand.objects.get(id=brand_id)
        profile, _ = BrandProfile.objects.get_or_create(brand=brand)
    except Brand.DoesNotExist:
        return Response(
            {'detail': 'Brand not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Mock in ST/SIT
    env = getattr(settings, 'ENVIRONMENT', getattr(settings, 'ENV_NAME', 'ST'))
    if env in ['ST', 'SIT'] and not profile.shopify_access_token:
        return Response({
            'connected': True,
            'shop': 'mock-shop.myshopify.com',
            'scopes': ['read_products', 'write_products'],
            'last_checked': None,
        })
    
    # Real status
    connected = bool(profile.shopify_access_token and profile.shopify_store)
    response = {
        'connected': connected,
    }
    
    if connected:
        response['shop'] = profile.shopify_store
        response['scopes'] = ['read_products', 'write_products', 'read_content', 'write_content']
        if profile.shopify_connected_at:
            response['last_checked'] = profile.shopify_connected_at.isoformat()
    
    return Response(response)


@api_view(['POST'])
@permission_classes([IsBrandManager])
def disconnect_view(request):
    """Disconnect Shopify store"""
    brand_id = request.data.get('brand_id') or getattr(request, 'brand_id', None)
    if not brand_id:
        return Response(
            {'detail': 'brand_id required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        from brands.models import Brand, BrandProfile
        brand = Brand.objects.get(id=brand_id)
        profile, _ = BrandProfile.objects.get_or_create(brand=brand)
    except Brand.DoesNotExist:
        return Response(
            {'detail': 'Brand not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # In ST/SIT, just no-op
    env = getattr(settings, 'ENVIRONMENT', getattr(settings, 'ENV_NAME', 'ST'))
    if env in ['ST', 'SIT']:
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    # Clear token
    profile.shopify_access_token = ''
    profile.shopify_store = ''
    profile.shopify_connected_at = None
    profile.save()
    
    # Create audit log (if model exists)
    try:
        from content.models import AuditLog
        AuditLog.objects.create(
            brand=brand,
            user=request.user,
            action='shopify_disconnect',
            resource_type='shopify',
            resource_id=str(brand_id),
            changes={'disconnected': True},
        )
    except (ImportError, AttributeError):
        pass  # AuditLog model not available
    
    return Response(status=status.HTTP_204_NO_CONTENT)

