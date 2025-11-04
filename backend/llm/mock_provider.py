"""
Mock LLM provider for ST/SIT/UAT
"""
from typing import Dict, List, Optional
from .providers import LLMProvider
from .schemas import ContentVariantSchema, SEOProposalSchema, BlueprintSchema, TemplateSchema


class MockLLMProvider(LLMProvider):
    """Deterministic mock LLM provider"""
    
    def generate_content(self, product_title: str, product_description: str, brand_tone: Dict, required_terms: List[str], forbidden_terms: List[str], variant_number: int) -> Dict:
        """Generate deterministic content variant"""
        return {
            'title': f"{product_title} - Premium Quality {variant_number}",
            'bullets': [
                f"High-quality {product_title.lower()}",
                f"Designed for excellence",
                f"Perfect for your needs",
            ],
            'long_description': f"This is a premium {product_title.lower()} designed with care. {product_description}",
        }
    
    def generate_seo(self, brand_name: str, scope: str, items: List[Dict]) -> Dict:
        """Generate deterministic SEO data"""
        return {
            'titles': {item['id']: f"{item.get('title', 'Product')} | {brand_name}" for item in items},
            'meta_descriptions': {item['id']: f"Shop {item.get('title', 'products')} at {brand_name}" for item in items},
            'h1_tags': {item['id']: item.get('title', 'Product') for item in items},
            'h2_tags': {item['id']: [f"About {item.get('title', 'Product')}"] for item in items},
            'h3_tags': {item['id']: [] for item in items},
            'alt_texts': {item['id']: f"{item.get('title', 'Product')} image" for item in items},
            'internal_links': {item['id']: [] for item in items},
            'json_ld': {item['id']: {'@type': 'Product', 'name': item.get('title', 'Product')} for item in items},
        }
    
    def generate_blueprint(self, brand_profile: Dict, ia_signatures: List[Dict]) -> Dict:
        """Generate site blueprint"""
        return {
            'navigation': [
                {'label': 'Home', 'url': '/'},
                {'label': 'Products', 'url': '/products'},
                {'label': 'About', 'url': '/about'},
            ],
            'homepage_sections': [
                {'type': 'hero', 'title': 'Welcome'},
                {'type': 'features', 'title': 'Features'},
                {'type': 'products', 'title': 'Featured Products'},
            ],
            'category_template': {
                'layout': 'grid',
                'filters': True,
            },
            'pdp_template': {
                'layout': 'standard',
                'sections': ['images', 'details', 'description', 'reviews'],
            },
            'theme_tokens': {
                'colors': {'primary': '#6366f1', 'secondary': '#8b5cf6'},
                'typography': {'font_family': 'Inter'},
                'spacing': {'base': '16px'},
            },
        }
    
    def generate_template(self, complexity: str, industry: str, brand_tone: Dict, competitor_refs: Optional[List[str]] = None) -> Dict:
        """Generate store template"""
        return {
            'meta': {
                'name': f'{complexity} {industry} Template',
                'description': f'A {complexity.lower()} template for {industry}',
                'complexity': complexity,
                'tags': [industry, complexity],
            },
            'theme_tokens': {
                'colors': {'primary': '#6366f1', 'secondary': '#8b5cf6'},
                'typography': {'font_family': 'Inter'},
                'spacing': {'base': '16px'},
                'radii': {'base': '8px'},
            },
            'sections': [
                {'key': 'hero', 'name': 'Hero', 'enabled': True, 'props_schema': {}},
                {'key': 'features', 'name': 'Features', 'enabled': True, 'props_schema': {}},
                {'key': 'products', 'name': 'Products', 'enabled': True, 'props_schema': {}},
            ],
            'compatibility': {
                'shopify': {
                    'sections_enabled': True,
                    'metafields': [],
                },
            },
        }

