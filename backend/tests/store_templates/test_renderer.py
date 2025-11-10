"""
Tests for template renderer agent
"""
import pytest
import json
from unittest.mock import patch, MagicMock
from django.test import override_settings

from agents.template_renderer_agent import render_template
from store_templates.models import Template, TemplateBuild


@pytest.mark.django_db
class TestTemplateRendererAgent:
    """Test template rendering functionality"""

    def test_render_builtin_template(self):
        """Test rendering a built-in template"""
        # Create a test template
        template = Template.objects.create(
            name='Test Template',
            slug='test-template',
            source='builtin',
            built_in_key='minimal_tailwind',
            complexity='Starter'
        )

        context = {
            'brand': {
                'name': 'Test Store',
                'description': 'A test store'
            },
            'products': [
                {
                    'title': 'Test Product',
                    'description': 'A test product',
                    'price': 29.99
                }
            ]
        }

        with patch('agents.template_renderer_agent.upload_file_bytes') as mock_upload:
            mock_upload.return_value = 'https://supabase.com/test-file.html'

            result = render_template(template.id, context, force=True)

            # Should create a TemplateBuild record
            build = TemplateBuild.objects.filter(template=template).first()
            assert build is not None
            assert build.build_status == 'SUCCESS'

            # Should return success result
            assert result['success'] == True
            assert 'public_url' in result
            assert result['template_id'] == template.id

    def test_template_caching(self):
        """Test that identical context uses cached builds"""
        template = Template.objects.create(
            name='Cache Test',
            slug='cache-test',
            source='builtin',
            built_in_key='minimal_tailwind'
        )

        context = {'brand': {'name': 'Test'}}

        # First render
        with patch('agents.template_renderer_agent.upload_file_bytes') as mock_upload:
            mock_upload.return_value = 'https://supabase.com/file1.html'
            result1 = render_template(template.id, context)

        # Second render with same context (should use cache)
        result2 = render_template(template.id, context)

        # Should return cached result
        assert result2.get('cached') == True
        assert result2['success'] == True

    def test_missing_template_error(self):
        """Test error handling for non-existent template"""
        result = render_template(99999, {})

        assert result['success'] == False
        assert 'error' in result

    def test_invalid_template_source(self):
        """Test error handling for invalid template source"""
        template = Template.objects.create(
            name='Invalid Source',
            slug='invalid-source',
            source='invalid_type'
        )

        result = render_template(template.id, {})

        assert result['success'] == False
        assert 'Unsupported template source' in result['error']

    @patch('agents.template_renderer_agent.Environment')
    def test_jinja_rendering_error(self, mock_env_class):
        """Test handling of Jinja2 template errors"""
        # Mock Jinja2 to raise an error
        mock_env = MagicMock()
        mock_template = MagicMock()
        mock_template.render.side_effect = Exception("Jinja error")
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        template = Template.objects.create(
            name='Jinja Error Test',
            slug='jinja-error',
            source='builtin',
            built_in_key='minimal_tailwind'
        )

        result = render_template(template.id, {}, force=True)

        assert result['success'] == False
        assert 'error' in result

    def test_context_hash_generation(self):
        """Test that context hashing works for idempotency"""
        from agents.template_renderer_agent import _summarize_context

        context = {
            'brand': {'name': 'Test'},
            'products': [{'title': 'Product 1'}, {'title': 'Product 2'}],
            'theme': {'colors': {'primary': '#000'}}
        }

        summary = _summarize_context(context)

        assert summary['brand'] == 'dict(1 keys)'
        assert summary['products'] == 'list(2 items)'
        assert summary['theme'] == 'dict(1 keys)'
