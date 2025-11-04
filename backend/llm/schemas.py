"""
Pydantic schemas for LLM output validation
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class ContentVariantSchema(BaseModel):
    """Content variant schema"""
    title: str = Field(..., max_length=255)
    bullets: List[str] = Field(..., min_items=3, max_items=5)
    long_description: str = Field(..., min_length=100)


class SEOProposalSchema(BaseModel):
    """SEO proposal schema"""
    titles: Dict[str, str]
    meta_descriptions: Dict[str, str]
    h1_tags: Dict[str, str]
    h2_tags: Dict[str, List[str]]
    h3_tags: Dict[str, List[str]]
    alt_texts: Dict[str, str]
    internal_links: Dict[str, List[str]]
    json_ld: Dict[str, Dict]


class BlueprintSchema(BaseModel):
    """Site blueprint schema"""
    navigation: List[Dict[str, str]]
    homepage_sections: List[Dict[str, str]]
    category_template: Dict
    pdp_template: Dict
    theme_tokens: Dict


class TemplateSchema(BaseModel):
    """Store template schema"""
    meta: Dict[str, str]
    theme_tokens: Dict
    sections: List[Dict]
    compatibility: Dict

