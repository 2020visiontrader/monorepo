# Template System Documentation

This document describes the template system for rendering dynamic e-commerce storefronts.

## Overview

The template system supports two types of templates:

1. **Built-in Templates**: Pre-defined templates included with the platform
2. **Uploaded Templates**: Custom templates uploaded by users as ZIP files

Templates use Jinja2 templating engine and are rendered with dynamic context data including brand information, products, and theme settings.

## Built-in Templates

### Available Templates

#### `minimal_tailwind`
- **Description**: Clean, modern template using Tailwind CSS
- **Features**: Hero section, product grid, responsive design
- **Best for**: Simple product catalogs and landing pages

#### `catalog_basic`
- **Description**: Product-focused catalog with search and filtering
- **Features**: Product grid, search functionality, availability indicators
- **Best for**: Large product catalogs requiring navigation

### Template Structure

Each built-in template directory contains:

```
template_name/
├── index.html.jinja    # Main template file
├── README.md          # Template documentation
└── [other assets]     # CSS, JS, images (if any)
```

## Template Variables

### Brand Context
```json
{
  "brand": {
    "name": "Store Name",
    "tagline": "Store Tagline",
    "description": "Store description",
    "contact_email": "contact@example.com"
  }
}
```

### Theme Configuration
```json
{
  "theme": {
    "colors": {
      "primary": "#007bff",
      "secondary": "#6c757d"
    },
    "typography": {
      "font_family": "Inter, sans-serif"
    }
  }
}
```

### Navigation
```json
{
  "navigation": [
    {"label": "Home", "url": "/"},
    {"label": "Products", "url": "/products"},
    {"label": "About", "url": "/about"}
  ]
}
```

### Products
```json
{
  "products": [
    {
      "title": "Product Name",
      "description": "Product description",
      "price": 29.99,
      "image_url": "/path/to/image.jpg",
      "availability": "in_stock",
      "category": "Category Name"
    }
  ]
}
```

## Uploaded Templates

### Requirements

Uploaded templates must be provided as ZIP files with the following structure:

```
template.zip
├── index.html.jinja          # Main template (required)
├── assets/                   # Static assets (optional)
│   ├── css/
│   ├── js/
│   └── images/
├── partials/                 # Template partials (optional)
│   ├── header.html.jinja
│   └── footer.html.jinja
└── README.md                 # Documentation (recommended)
```

### Upload Process

1. Create a ZIP file with the required structure
2. Upload via admin interface or API endpoint
3. Template is stored in `templates/raw` Supabase bucket
4. Template becomes available for rendering

### Security Considerations

- Uploaded templates are executed in a sandboxed environment
- No arbitrary code execution is allowed
- Only Jinja2 templating operations are permitted
- File system access is restricted

## Rendering Process

### Built-in Template Rendering

1. Load template files from `store_templates/builtins/{template_key}/`
2. Set up Jinja2 environment with custom filters
3. Render all `.jinja` files with provided context
4. Copy non-template files unchanged
5. Deploy rendered files to Supabase Storage

### Uploaded Template Rendering

1. Download ZIP from `templates/raw` bucket
2. Extract to temporary directory
3. Set up Jinja2 environment
4. Render template files with context
5. Deploy to `templates-rendered` bucket

## Management Commands

### Build Template

```bash
# Build with default context
python manage.py build_template --template_id 1

# Build with custom context file
python manage.py build_template --template_id 1 --context_file context.json

# Force rebuild
python manage.py build_template --template_id 1 --force

# Output as JSON
python manage.py build_template --template_id 1 --output_json
```

### Context File Format

```json
{
  "brand": {...},
  "theme": {...},
  "navigation": [...],
  "hero": {...},
  "products": [...]
}
```

## Supabase Storage

### Bucket Structure

- `templates/raw`: Uploaded template ZIP files
- `templates-rendered`: Rendered static websites
- `templates-data`: Build logs and metadata

### File Organization

```
templates-rendered/
├── template-slug/
│   ├── timestamp/
│   │   ├── index.html
│   │   ├── assets/
│   │   └── ...
```

## Custom Filters

The template system provides these Jinja2 filters:

- `truncate(length)`: Truncate text to specified length
- `currency`: Format prices (built-in)
- `date`: Format dates (built-in)

## Error Handling

### Common Issues

1. **Missing Context Variables**: Templates fail if required variables are missing
2. **Invalid Jinja2 Syntax**: Template compilation errors
3. **Supabase Upload Failures**: Network or permission issues
4. **File Encoding Problems**: Non-UTF8 files in uploaded templates

### Debugging

- Check `TemplateBuild` records for detailed error logs
- Use `--output_json` flag for structured error information
- Review TaskRun records for execution tracing

## Performance Considerations

- Templates are cached based on context hash
- Use `--force` flag to bypass caching
- Large templates may impact rendering time
- Consider CDN for static asset delivery

## Best Practices

1. **Validate Context**: Ensure all required variables are provided
2. **Test Templates**: Use management command to test rendering
3. **Version Control**: Keep template versions for rollback
4. **Optimize Assets**: Minimize and compress static files
5. **Monitor Builds**: Check TemplateBuild records regularly

## API Integration

Templates can be rendered programmatically:

```python
from agents.template_renderer_agent import render_template

result = render_template(
    template_id=1,
    context=context_data,
    target_bucket='templates-rendered'
)

if result['success']:
    site_url = result['public_url']
```

## Future Enhancements

- Template marketplace
- Live preview functionality
- Advanced theming system
- Multi-language support
- A/B testing framework
