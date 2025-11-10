# Minimal Tailwind Template

A clean, modern e-commerce template built with Tailwind CSS and Jinja2 templating.

## Features

- **Responsive Design**: Mobile-first approach with responsive grid layouts
- **Tailwind CSS**: Utility-first CSS framework loaded via CDN
- **Dynamic Theming**: Configurable colors and typography via template variables
- **Product Grid**: Clean product display with hover effects
- **Navigation**: Simple header navigation
- **Hero Section**: Gradient background with call-to-action
- **Footer**: Multi-column layout with links and contact info

## Template Variables

### Brand Data
```json
{
  "brand": {
    "name": "Your Store Name",
    "tagline": "Your Tagline",
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
      "primary": "#3b82f6",
      "secondary": "#64748b"
    },
    "typography": {
      "font_family": "Inter"
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

### Hero Section
```json
{
  "hero": {
    "title": "Welcome to Our Store",
    "subtitle": "Discover amazing products"
  }
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
      "image_url": "/path/to/image.jpg"
    }
  ]
}
```

## Build Process

This template uses Tailwind CSS loaded via CDN, so no build step is required for basic usage. For production optimization, consider:

1. Installing Tailwind CSS locally
2. Configuring a build process with PostCSS
3. Minifying the final CSS output

## Customization

- Modify the Tailwind config in the `<script>` tag for custom colors and fonts
- Update the component structure in the HTML
- Add custom CSS classes for additional styling
- Extend the Jinja2 template logic for dynamic content

## Browser Support

- Modern browsers with ES6 support
- Mobile browsers (iOS Safari, Chrome Mobile)
- Desktop browsers (Chrome, Firefox, Safari, Edge)
