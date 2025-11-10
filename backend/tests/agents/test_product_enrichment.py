"""
Tests for product enrichment agent
"""
import pytest
import uuid
from unittest.mock import patch, MagicMock

from agents.product_enrichment_agent import run_product_enrichment


@pytest.mark.django_db
class TestProductEnrichmentAgent:
    """Test product enrichment functionality"""

    @patch('agents.product_enrichment_agent.generate_text')
    @patch('agents.product_enrichment_agent.validate_content')
    @patch('agents.product_enrichment_agent.upload_file_bytes')
    def test_successful_product_enrichment(self, mock_upload, mock_validate, mock_generate):
        """Test successful product enrichment workflow"""
        # Mock AI responses
        mock_generate.side_effect = [
            {'text': 'Premium Wireless Bluetooth Headphones with Active Noise Cancellation', 'tokens_used': 15},
            {'text': 'Experience crystal-clear audio with our premium wireless headphones featuring advanced active noise cancellation technology.', 'tokens_used': 25},
            {'text': 'wireless headphones, noise cancelling, bluetooth, premium audio, wireless technology', 'tokens_used': 10}
        ]

        # Mock validation
        mock_validate.return_value = {'is_valid': True, 'score': 0.9}

        # Mock Supabase upload
        mock_upload.return_value = 'https://supabase.com/enrichment.json'

        product_id = str(uuid.uuid4())
        result = run_product_enrichment(product_id=product_id, dry_run=False)

        assert result['status'] == 'SUCCESS'
        assert result['product_id'] == product_id
        assert 'Premium Wireless Bluetooth Headphones' in result['enriched_title']
        assert result['content_quality_score'] == 0.9
        assert result['tokens_used'] == 50  # 15 + 25 + 10
        assert result['cached'] == False
        assert 'task_run_id' in result

        # Verify service calls
        assert mock_generate.call_count == 3  # title, description, keywords
        mock_validate.assert_called_once()
        assert mock_upload.call_count == 2  # enrichment data + cache

    @patch('agents.product_enrichment_agent.generate_text')
    def test_enrichment_with_cache_hit(self, mock_generate):
        """Test that cached results are used when available"""
        # Mock cache hit
        with patch('agents.product_enrichment_agent._check_prompt_cache') as mock_cache:
            mock_cache.return_value = {
                'title': 'Cached Title',
                'description': 'Cached Description',
                'seo_keywords': ['cached', 'keywords'],
                'tokens_used': 30
            }

            product_id = str(uuid.uuid4())
            result = run_product_enrichment(product_id=product_id)

            assert result['status'] == 'SUCCESS'
            assert result['enriched_title'] == 'Cached Title'
            assert result['cached'] == True

            # Should not call AI generation when cache hit
            mock_generate.assert_not_called()

    def test_product_not_found(self):
        """Test handling of non-existent products"""
        # Mock product not found
        with patch('agents.product_enrichment_agent._get_product_for_enrichment') as mock_get:
            mock_get.return_value = None

            product_id = str(uuid.uuid4())
            result = run_product_enrichment(product_id=product_id)

            assert result['status'] == 'FAILED'
            assert result['error_type'] == 'PRODUCT_NOT_FOUND'

    def test_already_enriched_product(self):
        """Test skipping already enriched products"""
        # Mock already enriched product
        with patch('agents.product_enrichment_agent._is_product_already_enriched') as mock_check:
            mock_check.return_value = True

            product_id = str(uuid.uuid4())
            result = run_product_enrichment(product_id=product_id)

            assert result['status'] == 'FAILED'
            assert result['error_type'] == 'ALREADY_ENRICHED'

    @patch('agents.product_enrichment_agent.validate_content')
    def test_content_validation_failure(self, mock_validate):
        """Test handling of content validation failures"""
        # Mock validation failure
        mock_validate.return_value = {
            'is_valid': False,
            'score': 0.3,
            'issues': ['Title too short', 'Description inadequate']
        }

        with patch('agents.product_enrichment_agent.generate_text') as mock_generate:
            mock_generate.side_effect = [
                {'text': 'Hi', 'tokens_used': 5},  # Too short title
                {'text': 'Short desc', 'tokens_used': 10},  # Too short description
                {'text': 'keyword1, keyword2', 'tokens_used': 5}
            ]

            product_id = str(uuid.uuid4())
            result = run_product_enrichment(product_id=product_id)

            assert result['status'] == 'FAILED'
            assert result['error_type'] == 'VALIDATION_FAILED'
            assert 'Content validation failed' in result['error']

    @patch('agents.product_enrichment_agent.generate_text')
    def test_ai_service_failure(self, mock_generate):
        """Test handling of AI service failures"""
        # Mock AI service failure
        mock_generate.side_effect = Exception("AI service unavailable")

        product_id = str(uuid.uuid4())
        result = run_product_enrichment(product_id=product_id)

        assert result['status'] == 'FAILED'
        assert result['error_type'] == 'ENRICHMENT_ERROR'
        assert 'AI service unavailable' in result['error']

    def test_dry_run_mode(self):
        """Test dry run mode doesn't save changes"""
        with patch('agents.product_enrichment_agent.generate_text') as mock_generate, \
             patch('agents.product_enrichment_agent.validate_content') as mock_validate, \
             patch('agents.product_enrichment_agent._save_enriched_product_data') as mock_save:

            mock_generate.side_effect = [
                {'text': 'Test Title', 'tokens_used': 10},
                {'text': 'Test Description', 'tokens_used': 20},
                {'text': 'keyword1, keyword2', 'tokens_used': 5}
            ]
            mock_validate.return_value = {'is_valid': True, 'score': 0.8}

            product_id = str(uuid.uuid4())
            result = run_product_enrichment(product_id=product_id, dry_run=True)

            assert result['status'] == 'SUCCESS'
            # Should not save data in dry run mode
            mock_save.assert_not_called()

    def test_force_enrichment_flag(self):
        """Test force flag bypasses enrichment checks"""
        with patch('agents.product_enrichment_agent._is_product_already_enriched') as mock_check, \
             patch('agents.product_enrichment_agent.generate_text') as mock_generate, \
             patch('agents.product_enrichment_agent.validate_content') as mock_validate:

            mock_check.return_value = True  # Would normally be skipped
            mock_generate.side_effect = [
                {'text': 'Forced Title', 'tokens_used': 10},
                {'text': 'Forced Description', 'tokens_used': 20},
                {'text': 'keyword1, keyword2', 'tokens_used': 5}
            ]
            mock_validate.return_value = {'is_valid': True, 'score': 0.8}

            product_id = str(uuid.uuid4())
            result = run_product_enrichment(product_id=product_id, force=True)

            assert result['status'] == 'SUCCESS'
            assert result['enriched_title'] == 'Forced Title'
            # Should bypass the "already enriched" check
            mock_check.assert_called()

    def test_keyword_parsing(self):
        """Test keyword extraction and parsing"""
        from agents.product_enrichment_agent import _parse_keywords

        # Test normal parsing
        keywords = _parse_keywords("wireless, headphones, bluetooth, audio")
        assert len(keywords) == 4
        assert 'wireless' in keywords

        # Test limit enforcement
        many_keywords = _parse_keywords(", ".join([f"kw{i}" for i in range(15)]))
        assert len(many_keywords) <= 10

        # Test filtering of short keywords
        filtered = _parse_keywords("a, wireless, b, headphones, c")
        assert 'a' not in filtered
        assert 'b' not in filtered
        assert 'c' not in filtered
        assert 'wireless' in filtered

    def test_prompt_hash_generation(self):
        """Test product hash generation for caching"""
        from agents.product_enrichment_agent import _calculate_product_hash

        product = {
            'title': 'Test Product',
            'description': 'Test Description',
            'category': 'Electronics',
            'brand': 'TestBrand',
            'features': ['feature1', 'feature2']
        }

        hash1 = _calculate_product_hash(product)
        hash2 = _calculate_product_hash(product)

        # Same input should produce same hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 hex length

        # Different input should produce different hash
        product['title'] = 'Different Title'
        hash3 = _calculate_product_hash(product)
        assert hash3 != hash1
