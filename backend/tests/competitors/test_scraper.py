"""
Tests for store scraper agent
"""
import pytest
from unittest.mock import patch, MagicMock
from django.test import override_settings

from agents.store_scraper_agent import (
    run_store_scrape,
    _check_robots_txt,
    _extract_price,
    _extract_title
)


@pytest.mark.django_db
class TestStoreScraperAgent:
    """Test store scraper functionality"""

    @patch('agents.store_scraper_agent.requests.get')
    def test_scrape_with_requests_basic(self, mock_get):
        """Test basic scraping with requests"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'''
        <html>
        <head><title>Test Product</title></head>
        <body>
        <h1>Test Product</h1>
        <span class="price">$29.99</span>
        <img src="/image1.jpg" alt="Product image">
        <p>In stock</p>
        </body>
        </html>
        '''
        mock_response.text = mock_response.content.decode()
        mock_get.return_value = mock_response

        result = run_store_scrape('https://example.com', render_js=False)

        assert result['title'] == 'Test Product'
        assert result['price'] == 29.99
        assert result['currency'] == 'USD'
        assert result['scrape_method'] == 'requests'

    @patch('agents.store_scraper_agent.requests.get')
    def test_robots_txt_check(self, mock_get):
        """Test robots.txt compliance checking"""
        mock_response = MagicMock()
        mock_response.read.return_value = "User-agent: *\nDisallow: /"
        mock_get.return_value = mock_response

        # Should return False for disallowed path
        assert _check_robots_txt('https://example.com/private') == False

    def test_price_extraction(self):
        """Test price extraction from HTML"""
        from bs4 import BeautifulSoup

        html = '<div><span>$123.45</span><span>£67.89</span><span>€99.99</span></div>'
        soup = BeautifulSoup(html, 'html.parser')

        price, currency = _extract_price(soup)
        assert price == 123.45
        assert currency == 'USD'

    def test_title_extraction(self):
        """Test title extraction"""
        from bs4 import BeautifulSoup

        html = '<html><head><title>Product Title</title></head></html>'
        soup = BeautifulSoup(html, 'html.parser')

        title = _extract_title(soup)
        assert title == 'Product Title'

    @patch('agents.store_scraper_agent.upload_file_bytes')
    @patch('agents.store_scraper_agent.requests.get')
    def test_image_upload_to_supabase(self, mock_get, mock_upload):
        """Test that images are uploaded to Supabase"""
        # Mock image download
        mock_img_response = MagicMock()
        mock_img_response.status_code = 200
        mock_img_response.content = b'fake_image_data'
        mock_get.return_value = mock_img_response

        # Mock Supabase upload
        mock_upload.return_value = 'https://supabase.com/uploaded-image.jpg'

        # Mock page response with image
        mock_page_response = MagicMock()
        mock_page_response.status_code = 200
        mock_page_response.content = b'''
        <html><body>
        <img src="https://example.com/image.jpg">
        </body></html>
        '''
        mock_page_response.text = mock_page_response.content.decode()

        with patch('agents.store_scraper_agent.requests.get', return_value=mock_page_response):
            result = run_store_scrape('https://example.com', render_js=False)

        # Should have called upload for the image
        mock_upload.assert_called()
        assert 'uploaded_images' in result

    def test_scraper_error_handling(self):
        """Test error handling for failed scrapes"""
        result = run_store_scrape('https://nonexistent-site-that-will-fail.com')

        assert result['success'] == False
        assert 'error' in result
        assert result['error_type'] == 'SCRAPING_ERROR'
