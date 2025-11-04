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

## Structure

- `backend/` - Django application
- `frontend/` - Next.js application
- `ops/` - Docker, CI/CD, environment configs
- `tests/` - E2E tests and fixtures

## Environments

- ST (Smoke Test) - Local development
- SIT (System Integration Test) - Integration testing
- UAT (User Acceptance Test) - Pre-production
- PROD - Production

## Features

- Multi-tenant Organizations & Brands
- Brand Onboarding with Competitor Analysis
- Website Builder (Site Blueprint)
- Product Copy Generation (LLM-powered)
- SEO Optimization Engine
- Marketing Frameworks Curation
- Shopify Integration
- Store Templates Library

