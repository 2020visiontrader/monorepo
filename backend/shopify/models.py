"""
Shopify integration models
"""
from django.db import models
import uuid


class ShopifyConnection(models.Model):
    """Shopify OAuth connection"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.OneToOneField('brands.Brand', on_delete=models.CASCADE, related_name='shopify_connection')
    
    shop = models.CharField(max_length=255)  # shop.myshopify.com
    access_token = models.TextField()
    scopes = models.JSONField(default=list)
    
    # OAuth state
    oauth_state = models.CharField(max_length=255, blank=True)
    oauth_code = models.CharField(max_length=255, blank=True)
    
    connected_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'shopify_connections'

    def __str__(self):
        return f"{self.brand.name} - {self.shop}"

