"""
Shopify API client
"""
import httpx
from django.conf import settings
from typing import Dict, Optional, List


class ShopifyClient:
    """Shopify API client with idempotency support"""
    
    def __init__(self, shop: str, access_token: str):
        self.shop = shop
        self.access_token = access_token
        self.api_version = settings.SHOPIFY_API_VERSION
        self.base_url = f"https://{shop}/admin/api/{self.api_version}"
        self.headers = {
            'X-Shopify-Access-Token': access_token,
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, idempotency_key: Optional[str] = None):
        """Make HTTP request with idempotency support"""
        url = f"{self.base_url}/{endpoint}"
        headers = self.headers.copy()
        
        if idempotency_key:
            headers['Idempotency-Key'] = idempotency_key
        
        response = httpx.request(
            method=method,
            url=url,
            headers=headers,
            json=data,
            timeout=30.0
        )
        response.raise_for_status()
        return response.json()
    
    def get_product(self, product_id: str) -> Dict:
        """Get product by ID"""
        return self._make_request('GET', f'products/{product_id}.json')
    
    def update_product(self, product_id: str, title: Optional[str] = None, description: Optional[str] = None, bullets: Optional[List[str]] = None, idempotency_key: Optional[str] = None) -> Dict:
        """Update product"""
        product_data = {}
        if title:
            product_data['title'] = title
        if description:
            product_data['body_html'] = description
        if bullets:
            # Convert bullets to HTML
            product_data['body_html'] = f"<ul>{''.join([f'<li>{b}</li>' for b in bullets])}</ul>"
        
        data = {'product': product_data}
        return self._make_request('PUT', f'products/{product_id}.json', data=data, idempotency_key=idempotency_key)
    
    def update_page(self, page_id: str, title: Optional[str] = None, body_html: Optional[str] = None, idempotency_key: Optional[str] = None) -> Dict:
        """Update page"""
        page_data = {}
        if title:
            page_data['title'] = title
        if body_html:
            page_data['body_html'] = body_html
        
        data = {'page': page_data}
        return self._make_request('PUT', f'pages/{page_id}.json', data=data, idempotency_key=idempotency_key)
    
    def update_metafield(self, metafield_id: str, value: str, idempotency_key: Optional[str] = None) -> Dict:
        """Update metafield"""
        data = {'metafield': {'id': metafield_id, 'value': value}}
        return self._make_request('PUT', f'metafields/{metafield_id}.json', data=data, idempotency_key=idempotency_key)

