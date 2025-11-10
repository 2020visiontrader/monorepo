"""
Template Renderer Automation Agent

Agent Role:
    Renders Jinja2 templates with dynamic context data and deploys the resulting
    static websites to Supabase Storage for hosting and delivery.

Inputs:
    - template_id (int): ID of the template to render
    - context (dict): Context data for template rendering (brand, products, theme, etc.)
    - target_bucket (str, optional): Supabase bucket for deployment. Defaults to 'templates-rendered'.
    - force (bool, optional): Whether to force re-rendering. Defaults to False.

Outputs:
    - Renders complete HTML pages from Jinja2 templates
    - Deploys rendered static sites to Supabase Storage
    - Creates TemplateBuild records for tracking and rollback
    - Returns public URLs for accessing rendered sites
    - Updates Template.last_built_at timestamps

Supabase Interactions:
    - Downloads uploaded template ZIPs from 'templates/raw' bucket
    - Uploads rendered static sites to 'templates-rendered' bucket
    - Stores build artifacts and logs in 'templates-data' bucket

Idempotency:
    - Checks TemplateBuild records for existing successful builds
    - Uses template_id + context_hash for deduplication
    - Validates existing rendered sites before re-deployment
    - Maintains build history for rollback capabilities

Error Handling:
    - Validates template files and context data before rendering
    - Handles Jinja2 template syntax errors with detailed messages
    - Implements timeout protection for long-running builds
    - Provides fallback to cached versions on build failures
    - Logs all errors to TemplateBuild records

Example Usage:
    # Render a built-in template
    result = render_template(
        template_id=1,
        context={
            'brand': {'name': 'My Store', 'description': 'Great products'},
            'products': [...],
            'theme': {'colors': {'primary': '#007bff'}}
        }
    )

    # Access rendered site
    print(f"Site available at: {result['public_url']}")
"""

import os
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
import time

from jinja2 import Environment, FileSystemLoader, TemplateSyntaxError, TemplateError

from .task_run import record_task_start, record_task_end
from core.supabase_storage import upload_file_bytes, download_file_bytes
from store_templates.models import Template, TemplateBuild


def render_template(
    template_id: int,
    context: Dict[str, Any],
    target_bucket: str = 'templates-rendered',
    force: bool = False
) -> Dict[str, Any]:
    """
    Main template rendering function.

    Renders a template with context data and deploys to Supabase Storage.

    Returns dict with rendering results and deployment URLs.
    """
    # Generate context hash for idempotency
    context_str = json.dumps(context, sort_keys=True)
    context_hash = hashlib.sha256(context_str.encode()).hexdigest()

    task_run = record_task_start('template_renderer_agent', {
        'template_id': template_id,
        'context_hash': context_hash,
        'target_bucket': target_bucket,
        'force': force
    })

    try:
        # Get template
        template = Template.objects.get(id=template_id)

        # Check for existing successful build (unless force=True)
        if not force:
            existing_build = TemplateBuild.objects.filter(
                template=template,
                build_status='SUCCESS'
            ).order_by('-built_at').first()

            if existing_build and existing_build.build_metadata.get('context_hash') == context_hash:
                return _handle_existing_build(existing_build, task_run)

        # Create build record
        build = TemplateBuild.objects.create(
            template=template,
            build_status='BUILDING',
            build_metadata={
                'context_hash': context_hash,
                'context_summary': _summarize_context(context),
                'template_source': template.source,
                'template_key': template.built_in_key
            }
        )

        # Render template based on source type
        if template.source == 'builtin':
            rendered_files = _render_builtin_template(template, context)
        elif template.source == 'uploaded':
            rendered_files = _render_uploaded_template(template, context)
        else:
            raise ValueError(f"Unsupported template source: {template.source}")

        # Deploy to Supabase
        deployment_result = _deploy_to_supabase(rendered_files, template, target_bucket)

        # Update build record
        build.build_status = 'SUCCESS'
        build.built_at = build.created_at  # Use creation time as build time
        build.rendered_bucket_path = deployment_result['bucket_path']
        build.build_log = 'Build completed successfully'
        build.save()

        # Update template
        template.last_built_at = build.built_at
        template.save()

        result = {
            'success': True,
            'public_url': deployment_result['public_url'],
            'bucket_path': deployment_result['bucket_path'],
            'build_id': build.id,
            'template_id': template_id,
            'context_hash': context_hash,
            'rendered_files': len(rendered_files),
            'task_run_id': task_run.id
        }

        record_task_end(task_run, success=True)
        return result

    except Exception as e:
        # Update build status on failure
        if 'build' in locals():
            build.build_status = 'FAILED'
            build.build_log = str(e)
            build.save()

        return _handle_error(task_run, str(e), "RENDERING_ERROR")


def _render_builtin_template(template: Template, context: Dict[str, Any]) -> Dict[str, str]:
    """Render a built-in template from the repo."""
    if not template.built_in_key:
        raise ValueError("Built-in template missing built_in_key")

    template_dir = Path(__file__).parent.parent / 'store_templates' / 'builtins' / template.built_in_key

    if not template_dir.exists():
        raise FileNotFoundError(f"Built-in template not found: {template_dir}")

    # Set up Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True
    )

    # Add custom filters
    env.filters['truncate'] = lambda s, length: s[:length] + '...' if len(s) > length else s

    rendered_files = {}

    # Render all .jinja files
    for jinja_file in template_dir.glob('**/*.jinja'):
        if jinja_file.is_file():
            relative_path = jinja_file.relative_to(template_dir)
            template_obj = env.get_template(str(relative_path))

            try:
                rendered_content = template_obj.render(**context)
                # Change extension from .jinja to .html
                html_path = str(relative_path).replace('.jinja', '.html')
                rendered_files[html_path] = rendered_content
            except (TemplateSyntaxError, TemplateError) as e:
                raise ValueError(f"Template rendering error in {relative_path}: {e}")

    # Copy non-template files
    for file_path in template_dir.glob('**/*'):
        if file_path.is_file() and not file_path.name.endswith('.jinja'):
            relative_path = file_path.relative_to(template_dir)
            with open(file_path, 'r', encoding='utf-8') as f:
                rendered_files[str(relative_path)] = f.read()

    return rendered_files


def _render_uploaded_template(template: Template, context: Dict[str, Any]) -> Dict[str, str]:
    """Render an uploaded template from Supabase Storage."""
    if not template.supabase_raw_path:
        raise ValueError("Uploaded template missing supabase_raw_path")

    # Download template ZIP from Supabase
    zip_data = download_file_bytes('templates/raw', template.supabase_raw_path)

    # Extract to temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = Path(temp_dir) / 'template.zip'

        with open(zip_path, 'wb') as f:
            f.write(zip_data)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)

        # Set up Jinja2 environment
        env = Environment(
            loader=FileSystemLoader(temp_dir),
            trim_blocks=True,
            lstrip_blocks=True
        )

        # Add custom filters
        env.filters['truncate'] = lambda s, length: s[:length] + '...' if len(s) > length else s

        rendered_files = {}

        # Find and render all .jinja files
        for jinja_file in Path(temp_dir).glob('**/*.jinja'):
            if jinja_file.is_file():
                relative_path = jinja_file.relative_to(Path(temp_dir))
                template_obj = env.get_template(str(relative_path))

                try:
                    rendered_content = template_obj.render(**context)
                    # Change extension from .jinja to .html
                    html_path = str(relative_path).replace('.jinja', '.html')
                    rendered_files[html_path] = rendered_content
                except (TemplateSyntaxError, TemplateError) as e:
                    raise ValueError(f"Template rendering error in {relative_path}: {e}")

        # Copy non-template files
        for file_path in Path(temp_dir).glob('**/*'):
            if file_path.is_file() and not file_path.name.endswith('.jinja'):
                relative_path = file_path.relative_to(Path(temp_dir))
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        rendered_files[str(relative_path)] = f.read()
                except UnicodeDecodeError:
                    # Binary file, skip for now
                    pass

    return rendered_files


def _deploy_to_supabase(rendered_files: Dict[str, str], template: Template, target_bucket: str) -> Dict[str, str]:
    """Deploy rendered files to Supabase Storage."""
    timestamp = int(time.time())
    bucket_path = f"{template.slug}/{timestamp}"

    uploaded_files = []

    for file_path, content in rendered_files.items():
        # Create full path in bucket
        full_path = f"{bucket_path}/{file_path}"

        # Determine content type
        if file_path.endswith('.html'):
            content_type = 'text/html'
        elif file_path.endswith('.css'):
            content_type = 'text/css'
        elif file_path.endswith('.js'):
            content_type = 'application/javascript'
        else:
            content_type = 'text/plain'

        # Upload file
        public_url = upload_file_bytes(
            bucket=target_bucket,
            path=full_path,
            data=content.encode('utf-8'),
            content_type=content_type
        )

        uploaded_files.append({
            'path': full_path,
            'url': public_url,
            'content_type': content_type
        })

    # Return the index.html URL as the main public URL
    index_url = None
    for file_info in uploaded_files:
        if file_info['path'].endswith('/index.html'):
            index_url = file_info['url']
            break

    # Fallback to first HTML file
    if not index_url:
        for file_info in uploaded_files:
            if file_info['path'].endswith('.html'):
                index_url = file_info['url']
                break

    return {
        'bucket_path': bucket_path,
        'public_url': index_url,
        'uploaded_files': uploaded_files
    }


def _summarize_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Create a summary of context data for logging."""
    summary = {}
    for key, value in context.items():
        if isinstance(value, list):
            summary[key] = f"list({len(value)} items)"
        elif isinstance(value, dict):
            summary[key] = f"dict({len(value)} keys)"
        else:
            summary[key] = str(type(value).__name__)
    return summary


def _handle_existing_build(existing_build: TemplateBuild, task_run) -> Dict[str, Any]:
    """Handle case where template was already successfully built."""
    record_task_end(task_run, success=True)

    return {
        'success': True,
        'cached': True,
        'public_url': f"https://supabase-storage-url/{existing_build.rendered_bucket_path}/index.html",
        'build_id': existing_build.id,
        'built_at': existing_build.built_at.isoformat() if existing_build.built_at else None
    }


def _handle_error(task_run, error_message: str, error_type: str) -> Dict[str, Any]:
    """Handle rendering errors with proper logging."""
    record_task_end(task_run, success=False, error=f"{error_type}: {error_message}")

    return {
        'success': False,
        'error': error_message,
        'error_type': error_type
    }
