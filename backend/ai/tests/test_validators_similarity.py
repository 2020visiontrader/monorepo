"""
Tests for similarity and lexicon validators
"""
import pytest
from ai.validators import check_similarity, check_lexicon, check_similarity_batch


def test_check_similarity_identical():
    """Test similarity for identical texts"""
    text1 = "This is a test product title"
    text2 = "This is a test product title"
    
    similarity = check_similarity(text1, text2)
    assert similarity >= 0.9  # Should be very similar


def test_check_similarity_different():
    """Test similarity for different texts"""
    text1 = "This is a test product title"
    text2 = "Completely different content here"
    
    similarity = check_similarity(text1, text2)
    assert similarity < 0.5  # Should be low


def test_check_lexicon_passes():
    """Test lexicon check passes when no forbidden terms"""
    content = "This is a great product with amazing features"
    required_terms = ['product', 'features']
    forbidden_terms = ['bad', 'terrible']
    
    result = check_lexicon(content, required_terms, forbidden_terms)
    assert result['passed'] is True
    assert len(result['forbidden_found']) == 0
    assert len(result['required_found']) == 2


def test_check_lexicon_fails_forbidden():
    """Test lexicon check fails when forbidden term found"""
    content = "This is a bad product"
    required_terms = []
    forbidden_terms = ['bad', 'terrible']
    
    result = check_lexicon(content, required_terms, forbidden_terms)
    assert result['passed'] is False
    assert len(result['forbidden_found']) > 0
    assert 'bad' in result['forbidden_found']


def test_check_similarity_batch_passes():
    """Test similarity batch check passes when below threshold"""
    texts = [
        "Product A with amazing features",
        "Product B with different benefits",
        "Product C with unique qualities",
    ]
    
    result = check_similarity_batch(texts, threshold=0.9)
    assert result['passed'] is True  # Should be below 0.9
    assert result['max_similarity'] < 0.9


def test_check_similarity_batch_fails():
    """Test similarity batch check fails when above threshold"""
    texts = [
        "This is a test product title",
        "This is a test product title",  # Duplicate
    ]
    
    result = check_similarity_batch(texts, threshold=0.9)
    assert result['passed'] is False  # Should be above 0.9
    assert result['max_similarity'] >= 0.9

