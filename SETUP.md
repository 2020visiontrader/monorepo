# Setup Guide

## Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local backend development)
- Node.js 20+ and pnpm (for local frontend development)

## Quick Start with Docker

1. **Clone and navigate to the monorepo:**
   ```bash
   cd monorepo
   ```

2. **Set up environment variables:**
   ```bash
   cp ops/.env.example ops/.env
   # Edit ops/.env with your configuration
   ```

3. **Start all services:**
   ```bash
   cd ops
   docker-compose up -d
   ```

4. **Run migrations:**
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

5. **Seed demo data:**
   ```bash
   docker-compose exec backend python manage.py seed_demo
   ```

6. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Admin: http://localhost:8000/admin (login with demo@example.com / demo123)

## Local Development

### Backend

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Install Poetry (if not installed):**
   ```bash
   pip install poetry
   ```

3. **Install dependencies:**
   ```bash
   poetry install
   ```

4. **Set up environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your local settings
   ```

5. **Run migrations:**
   ```bash
   poetry run python manage.py migrate
   ```

6. **Start development server:**
   ```bash
   poetry run python manage.py runserver
   ```

7. **Start Celery worker (in another terminal):**
   ```bash
   poetry run celery -A config worker -l info
   ```

### Frontend

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Install pnpm (if not installed):**
   ```bash
   npm install -g pnpm
   ```

3. **Install dependencies:**
   ```bash
   pnpm install
   ```

4. **Start development server:**
   ```bash
   pnpm dev
   ```

## Environment Variables

### Backend (.env)

- `ENVIRONMENT`: ST, SIT, UAT, or PROD
- `DB_NAME`: PostgreSQL database name
- `DB_USER`: PostgreSQL user
- `DB_PASSWORD`: PostgreSQL password
- `DB_HOST`: PostgreSQL host
- `CELERY_BROKER_URL`: Redis URL for Celery
- `SECRET_KEY`: Django secret key
- `SHOPIFY_API_KEY`: Shopify API key
- `SHOPIFY_API_SECRET`: Shopify API secret
- `LLM_PROVIDER`: mock, openai, or anthropic
- `LLM_USE_MOCK`: Set to True for ST/SIT/UAT

### Frontend (.env.local)

- `NEXT_PUBLIC_API_URL`: Backend API URL
- `NEXT_PUBLIC_ENV`: Environment (ST/SIT/UAT/PROD)

## Testing

### Backend Tests
```bash
cd backend
poetry run pytest
```

### Frontend Tests
```bash
cd frontend
pnpm test
```

## CI/CD

The project includes GitHub Actions workflows for:
- Linting (ruff, black, eslint)
- Type checking (mypy, tsc)
- Running tests
- Building applications

See `.github/workflows/ci.yml` for details.

## Project Structure

```
monorepo/
├── backend/          # Django application
│   ├── core/        # Multitenancy & RBAC
│   ├── brands/      # Brand management
│   ├── competitors/ # Competitor analysis
│   ├── content/     # Content generation
│   ├── seo/         # SEO optimization
│   ├── frameworks/  # Marketing frameworks
│   ├── shopify/     # Shopify integration
│   ├── llm/         # LLM abstraction
│   └── store_templates/ # Store templates
├── frontend/        # Next.js application
├── ops/            # Docker & deployment configs
└── tests/          # E2E tests & fixtures
```

## Next Steps

1. Configure your Shopify API credentials
2. Set up proper authentication (currently using basic session auth)
3. Configure LLM provider for production
4. Set up proper error tracking and logging
5. Configure production database and Redis
6. Set up SSL/TLS certificates
7. Configure domain and DNS

