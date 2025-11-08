"""
Brand onboarding views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Brand

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def onboarding_status(request, brand_id):
    """Get onboarding status and next steps"""
    brand = get_object_or_404(Brand, id=brand_id)
    profile = brand.profile
    
    return Response({
        'current_step': profile.onboarding_step,
        'completed_steps': profile.completed_steps,
        'next_steps': profile.next_steps,
        'is_complete': profile.is_onboarding_complete
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_onboarding_step(request, brand_id):
    """Save response for current onboarding step"""
    brand = get_object_or_404(Brand, id=brand_id)
    profile = brand.profile
    
    step = request.data.get('step')
    if step != profile.onboarding_step:
        return Response(
            {'detail': f'Cannot save data for step {step}, current step is {profile.onboarding_step}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    data = request.data.get('data', {})
    
    # Update profile based on step
    if step == 'mission':
        profile.mission = data.get('mission', '')
        
    elif step == 'categories':
        profile.categories = data.get('categories', [])
        
    elif step == 'personas':
        profile.personas = data.get('personas', [])
        
    elif step == 'tone':
        profile.tone_sliders = data.get('tone_sliders', {})
        profile.required_terms = data.get('required_terms', [])
        profile.forbidden_terms = data.get('forbidden_terms', [])
        
    elif step == 'products':
        profile.single_sku = data.get('single_sku', False)
        
    elif step == 'shopify':
        if data.get('connected'):
            profile.shopify_store = data.get('store', '')
            profile.shopify_access_token = data.get('access_token', '')
            profile.shopify_connected_at = data.get('connected_at')
    
    # Update onboarding progress
    if step not in profile.completed_steps:
        profile.completed_steps = list(set(profile.completed_steps + [step]))
    
    # Move to next step
    all_steps = ['mission', 'categories', 'personas', 'tone', 'products', 'shopify']
    current_idx = all_steps.index(step)
    if current_idx < len(all_steps) - 1:
        profile.onboarding_step = all_steps[current_idx + 1]
    
    # Check if all required steps are complete
    required_steps = {'mission', 'categories', 'personas', 'tone', 'products'}
    if all(step in profile.completed_steps for step in required_steps):
        profile.is_onboarding_complete = True
    
    profile.save()
    
    return Response({
        'current_step': profile.onboarding_step,
        'completed_steps': profile.completed_steps,
        'next_steps': profile.next_steps,
        'is_complete': profile.is_onboarding_complete
    })