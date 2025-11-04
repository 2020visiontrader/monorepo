"""
Pydantic schemas and lint helpers for AI frameworks
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class ContentVariantSchema(BaseModel):
    """Schema for content variant validation"""
    product_id: str
    field_name: str
    variant_number: int = Field(ge=1, le=3)
    content: str
    is_valid: bool = True
    validation_errors: List[str] = []


class SEOOptimizationSchema(BaseModel):
    """Schema for SEO optimization validation"""
    title: str = Field(max_length=60)
    meta_description: str = Field(max_length=160)
    h1: str
    h2: List[str] = []
    h3: List[str] = []
    keywords: List[str] = []
    score: int = Field(ge=0, le=100)


class BlueprintSchema(BaseModel):
    """Schema for blueprint validation"""
    sections: List[Dict[str, Any]]
    theme_tokens: Dict[str, Any]


def validate_content_variant(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate content variant data"""
    try:
        ContentVariantSchema(**data)
        return True, []
    except Exception as e:
        return False, [str(e)]


def validate_seo(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate SEO data"""
    try:
        SEOOptimizationSchema(**data)
        return True, []
    except Exception as e:
        return False, [str(e)]


def validate_blueprint(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """Validate blueprint data"""
    try:
        BlueprintSchema(**data)
        return True, []
    except Exception as e:
        return False, [str(e)]


def check_similarity(text1: str, text2: str) -> float:
    """
    Calculate cosine similarity between two texts
    Returns value between 0 (no similarity) and 1 (identical)
    """
    if not text1 or not text2:
        return 0.0
    
    if SKLEARN_AVAILABLE:
        try:
            vectorizer = TfidfVectorizer()
            vectors = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(vectors[0:1], vectors[1:2])[0][0]
            return float(similarity)
        except Exception:
            pass
    
    # Fallback: simple word overlap (Jaccard similarity)
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union) if union else 0.0


def check_lexicon(
    content: str,
    required_terms: List[str],
    forbidden_terms: List[str],
) -> Dict[str, Any]:
    """
    Check lexicon policy compliance
    Returns: {passed: bool, required_found: List[str], forbidden_found: List[str]}
    """
    content_lower = content.lower()
    
    required_found = [term for term in required_terms if term.lower() in content_lower]
    forbidden_found = [term for term in forbidden_terms if term.lower() in content_lower]
    
    passed = len(forbidden_found) == 0  # Must have no forbidden terms
    
    return {
        'passed': passed,
        'required_found': required_found,
        'forbidden_found': forbidden_found,
        'required_missing': [t for t in required_terms if t.lower() not in content_lower],
    }


def check_similarity_batch(texts: List[str], threshold: float = 0.9) -> Dict[str, Any]:
    """
    Check similarity across a batch of texts
    Returns: {passed: bool, max_similarity: float, pairs: List[tuple]}
    """
    if len(texts) < 2:
        return {'passed': True, 'max_similarity': 0.0, 'pairs': []}
    
    max_sim = 0.0
    max_pair = None
    
    for i in range(len(texts)):
        for j in range(i + 1, len(texts)):
            sim = check_similarity(texts[i], texts[j])
            if sim > max_sim:
                max_sim = sim
                max_pair = (i, j)
    
    passed = max_sim < threshold
    
    return {
        'passed': passed,
        'max_similarity': max_sim,
        'pairs': [max_pair] if max_pair else [],
        'threshold': threshold,
    }

