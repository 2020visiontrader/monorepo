"""
Authentication views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, RoleAssignment
from .serializers import UserSerializer, RoleAssignmentSerializer


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'detail': 'Email and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = authenticate(request, username=user.username, password=password)
    if user is None:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    login(request, user)
    
    # Get user's roles and brands
    roles = RoleAssignment.objects.filter(user=user)
    orgs = [role.organization for role in roles if role.organization]
    brands = []
    for role in roles:
        if role.brand_id:
            from brands.models import Brand
            try:
                brands.append(Brand.objects.get(id=role.brand_id))
            except Brand.DoesNotExist:
                pass
    
    return Response({
        'user': UserSerializer(user).data,
        'roles': [RoleAssignmentSerializer(role).data for role in roles],
        'orgs': [{'id': str(org.id), 'name': org.name} for org in orgs],
        'brands': [{'id': str(brand.id), 'name': brand.name} for brand in brands],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout"""
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Get current user info"""
    user = request.user
    roles = RoleAssignment.objects.filter(user=user)
    orgs = [role.organization for role in roles if role.organization]
    brands = []
    for role in roles:
        if role.brand_id:
            from brands.models import Brand
            try:
                brands.append(Brand.objects.get(id=role.brand_id))
            except Brand.DoesNotExist:
                pass
    
    return Response({
        'user': UserSerializer(user).data,
        'roles': [RoleAssignmentSerializer(role).data for role in roles],
        'orgs': [{'id': str(org.id), 'name': org.name} for org in orgs],
        'brands': [{'id': str(brand.id), 'name': brand.name} for brand in brands],
    })

