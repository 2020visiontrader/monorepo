"""
Tests for BrandProfile onboarding functionality
"""
from django.test import TestCase
from django.db import transaction
from brands.models import Brand, BrandProfile
from core.models import Organization

class BrandProfileOnboardingTests(TestCase):
    def setUp(self):
        self.org = Organization.objects.create(name='Test Org')
        self.brand = Brand.objects.create(
            organization=self.org,
            name='Test Brand',
            slug='test-brand'
        )
        self.profile = BrandProfile.objects.create(brand=self.brand)

    def test_sync_onboarding_mission(self):
        """Test syncing mission step data"""
        response_data = {
            'step': 'mission',
            'data': {
                'mission': 'To make sustainable products accessible'
            }
        }
        self.profile.sync_onboarding_responses(response_data)
        
        # Check profile updates
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.mission, 'To make sustainable products accessible')
        self.assertIn('mission', self.profile.completed_steps)
        self.assertEqual(
            self.profile.brand_identity['mission'],
            {'mission': 'To make sustainable products accessible'}
        )
        self.assertFalse(self.profile.is_onboarding_complete)

    def test_sync_onboarding_categories(self):
        """Test syncing categories step data"""
        response_data = {
            'step': 'categories',
            'data': {
                'categories': ['Sustainable', 'Eco-friendly']
            }
        }
        self.profile.sync_onboarding_responses(response_data)
        
        # Check profile updates
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.categories, ['Sustainable', 'Eco-friendly'])
        self.assertIn('categories', self.profile.completed_steps)
        self.assertEqual(
            self.profile.brand_identity['categories'],
            {'categories': ['Sustainable', 'Eco-friendly']}
        )
        self.assertFalse(self.profile.is_onboarding_complete)

    def test_sync_onboarding_personas(self):
        """Test syncing personas step data"""
        response_data = {
            'step': 'personas',
            'data': {
                'personas': [
                    {'name': 'Eco Conscious Consumer', 'age': '25-34'}
                ]
            }
        }
        self.profile.sync_onboarding_responses(response_data)
        
        # Check profile updates
        self.profile.refresh_from_db()
        self.assertEqual(len(self.profile.personas), 1)
        self.assertEqual(self.profile.personas[0]['name'], 'Eco Conscious Consumer')
        self.assertIn('personas', self.profile.completed_steps)
        self.assertEqual(
            self.profile.brand_identity['personas'],
            {'personas': [{'name': 'Eco Conscious Consumer', 'age': '25-34'}]}
        )
        self.assertFalse(self.profile.is_onboarding_complete)

    def test_sync_onboarding_tone(self):
        """Test syncing tone step data"""
        response_data = {
            'step': 'tone',
            'data': {
                'tone_sliders': {'professional': 0.8, 'friendly': 0.6},
                'required_terms': ['sustainable', 'eco-friendly'],
                'forbidden_terms': ['cheap']
            }
        }
        self.profile.sync_onboarding_responses(response_data)
        
        # Check profile updates
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.tone_sliders['professional'], 0.8)
        self.assertEqual(self.profile.required_terms, ['sustainable', 'eco-friendly'])
        self.assertEqual(self.profile.forbidden_terms, ['cheap'])
        self.assertIn('tone', self.profile.completed_steps)
        self.assertEqual(self.profile.brand_identity['tone'], response_data['data'])
        self.assertFalse(self.profile.is_onboarding_complete)

    def test_sync_onboarding_products(self):
        """Test syncing products step data"""
        response_data = {
            'step': 'products',
            'data': {
                'single_sku': True
            }
        }
        self.profile.sync_onboarding_responses(response_data)
        
        # Check profile updates
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.single_sku)
        self.assertIn('products', self.profile.completed_steps)
        self.assertEqual(
            self.profile.brand_identity['products'],
            {'single_sku': True}
        )
        self.assertFalse(self.profile.is_onboarding_complete)

    def test_sync_onboarding_completion(self):
        """Test onboarding completion after all required steps"""
        required_steps = {
            'mission': {'mission': 'Our mission'},
            'categories': {'categories': ['Cat1']},
            'personas': {'personas': [{'name': 'Persona1'}]},
            'tone': {'tone_sliders': {'prof': 0.5}},
            'products': {'single_sku': False}
        }
        
        for step, data in required_steps.items():
            response_data = {'step': step, 'data': data}
            self.profile.sync_onboarding_responses(response_data)
        
        # Check completion state
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.is_onboarding_complete)
        for step in required_steps:
            self.assertIn(step, self.profile.completed_steps)
            self.assertIn(step, self.profile.brand_identity)

    def test_sync_onboarding_shopify(self):
        """Test syncing optional Shopify step data"""
        response_data = {
            'step': 'shopify',
            'data': {
                'connected': True,
                'store': 'test-store.myshopify.com',
                'access_token': 'test-token',
                'connected_at': '2023-01-01T00:00:00Z'
            }
        }
        self.profile.sync_onboarding_responses(response_data)
        
        # Check profile updates
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.shopify_store, 'test-store.myshopify.com')
        self.assertEqual(self.profile.shopify_access_token, 'test-token')
        self.assertIn('shopify', self.profile.completed_steps)
        self.assertEqual(self.profile.brand_identity['shopify'], response_data['data'])
        self.assertFalse(self.profile.is_onboarding_complete)  # Shopify is optional

    def test_next_steps_progression(self):
        """Test next_steps property shows correct progression"""
        # Initial state
        steps = self.profile.next_steps
        self.assertEqual(len(steps), 6)  # All steps shown
        self.assertTrue(steps[0]['can_access'])  # First step accessible
        self.assertFalse(steps[1]['can_access'])  # Other steps locked
        
        # Complete first step
        self.profile.sync_onboarding_responses({
            'step': 'mission',
            'data': {'mission': 'Test mission'}
        })
        
        steps = self.profile.next_steps
        self.assertTrue(steps[1]['can_access'])  # Second step now accessible
        self.assertFalse(steps[2]['can_access'])  # Later steps still locked