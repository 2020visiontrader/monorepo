# AI-Powered E-Commerce Optimization Platform

Production-ready monorepo for an AI-powered e-commerce optimization app that integrates with Shopify.

## Architecture

- **Backend**: Django 5 + DRF + Celery + Redis + Postgres
- **Frontend**: Next.js 14 (App Router) + Tailwind + Radix UI
- **Ops**: Docker + docker-compose + GitHub Actions CI

## Quick Start

```bash
# Start all services
docker-compose up

# Run migrations
docker-compose exec backend python manage.py migrate

# Seed demo data
docker-compose exec backend python manage.py seed_demo

# Access services
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# Admin: http://localhost:8000/admin
```

## Development

### Backend
```bash
cd backend
poetry install
poetry run python manage.py runserver
```

### Frontend
```bash
cd frontend
pnpm install
pnpm dev
```

## Project Structure

```
backend/                    # Django application
├── agents/                 # Background automation agents (one per feature)
│   ├── brands_agent.py     # Brand management automation
│   ├── ai_agent.py         # AI & content generation automation
│   ├── competitors_agent.py # Competitor analysis automation
│   └── ...
├── config/                 # Django settings & configuration
├── core/                   # Core & authentication app
├── brands/                 # Brand management app
├── ai/                     # AI & content generation app
├── competitors/            # Competitor analysis app
├── content/                # Content management app
├── seo/                    # SEO optimization app
├── shopify/                # Shopify integration app
├── llm/                    # Language model integration app
├── store_templates/        # Template management app
├── dashboard/              # Dashboard app
├── onboarding/             # User onboarding app
├── staticfiles/            # Frontend assets (Tailwind, Alpine, images)
├── tests/                  # Global test utilities
├── management/             # Django management commands
├── docs/                   # Documentation & onboarding guides
└── README.md              # Project overview and setup instructions

frontend/                   # Next.js application
ops/                        # Docker, CI/CD, environment configs
tests/                      # E2E tests and fixtures
```

## Environments

- ST (Smoke Test) - Local development
- SIT (System Integration Test) - Integration testing
- UAT (User Acceptance Test) - Pre-production
- PROD - Production

## Features

- **Multi-tenant Organizations & Brands** - Isolated brand management
- **Brand Onboarding with Competitor Analysis** - Automated competitor research
- **Website Builder (Site Blueprint)** - Drag-and-drop site creation
- **Product Copy Generation (LLM-powered)** - AI content creation
- **SEO Optimization Engine** - Automated SEO improvements
- **Marketing Frameworks Curation** - Proven marketing strategies
- **Shopify Integration** - Seamless e-commerce connection
- **Store Templates Library** - Pre-built design templates

## Agent System

Background automation agents handle complex workflows:

- **brands_agent.py** - Brand onboarding, profile updates, migrations
- **ai_agent.py** - Content generation, model training, validation
- **competitors_agent.py** - Website monitoring, competitive intelligence
- **shopify_agent.py** - Store synchronization, order processing
- **seo_agent.py** - SEO analysis, optimization tasks

Run agents with: `python manage.py run_agents`

## Environment Setup

### Required Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DB_NAME=ecommerce_optimizer
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Supabase (for production data storage)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-key

# AI/LLM Configuration
LLM_PROVIDER=openai  # or 'mock' for development
LLM_API_KEY=your-openai-api-key
LLM_MODEL=gpt-4-turbo-preview

# Shopify Integration
SHOPIFY_API_KEY=your-shopify-api-key
SHOPIFY_API_SECRET=your-shopify-secret
SHOPIFY_REDIRECT_URI=http://localhost:8000/api/shopify/callback

# Redis/Celery
CELERY_BROKER_URL=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/1
```

### Development Setup

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd monorepo
   ```

2. **Backend setup:**
   ```bash
   cd backend
   poetry install
   cp .env.st.example .env  # Copy environment template
   poetry run python manage.py migrate
   poetry run python manage.py seed_demo_data
   ```

3. **Frontend setup:**
   ```bash
   cd frontend
   pnpm install
   cp .env.local.example .env.local
   ```

4. **Run development servers:**
   ```bash
   # Backend (terminal 1)
   cd backend && poetry run python manage.py runserver

   # Frontend (terminal 2)
   cd frontend && pnpm dev

   # Redis/Celery (terminal 3, optional)
   redis-server
   cd backend && poetry run celery worker -A config.celery
   ```

### Testing

```bash
cd backend
poetry run pytest -v --cov=.  # Run all tests with coverage
poetry run pytest tests/test_auth.py -v  # Run specific test file
```
