# Local Development Environment Status

## Environment: Local Dev (ST)

**Status:** ✅ Development servers running

## Services Status

| Service | Status | Port | Process |
|---------|--------|------|---------|
| Backend API (Dev) | ✅ Running | 8001 | Local (Poetry) |
| Frontend (Dev) | ✅ Running | 3001 | Local (pnpm) |
| Celery Worker | ✅ Running | - | Local (Poetry) |
| PostgreSQL | ✅ Running | 5432 | Docker |
| Redis | ✅ Running | 6379 | Docker |

## Access URLs

- **Frontend (Dev):** http://localhost:3001
- **Backend API (Dev):** http://localhost:8001
- **Admin Panel (Dev):** http://localhost:8001/admin

**Note:** Docker ST environment is also running on ports 8000/3000

## Development Setup

### Backend
- **Location:** `backend/`
- **Environment:** `.env` (configured for localhost DB/Redis)
- **Command:** `poetry run python manage.py runserver 8001`
- **Logs:** `/tmp/backend_dev.log`

### Frontend
- **Location:** `frontend/`
- **Environment:** `.env.local` (configured for backend on 8001)
- **Command:** `PORT=3001 pnpm dev`
- **Logs:** `/tmp/frontend_dev.log`

### Celery Worker
- **Location:** `backend/`
- **Command:** `poetry run celery -A config worker -l info`
- **Logs:** `/tmp/celery_dev.log`

## Database & Cache

- **PostgreSQL:** Running in Docker (localhost:5432)
- **Redis:** Running in Docker (localhost:6379)
- **Database:** ecommerce_optimizer
- **Migrations:** Up to date

## Demo Credentials

- **Email:** admin@demo.com
- **Password:** password123!
- **Role:** ORG_ADMIN

## Environment Configuration

- **ENVIRONMENT:** ST
- **DEBUG:** True
- **AI Mode:** MOCK (no API key - safe for testing)
- **Backend Port:** 8001 (to avoid conflict with Docker)
- **Frontend Port:** 3001 (to avoid conflict with Docker)

## Quick Commands

```bash
# Start backend dev server
cd backend
poetry run python manage.py runserver 8001

# Start frontend dev server
cd frontend
PORT=3001 pnpm dev

# Start Celery worker
cd backend
poetry run celery -A config worker -l info

# View logs
tail -f /tmp/backend_dev.log
tail -f /tmp/frontend_dev.log
tail -f /tmp/celery_dev.log

# Stop processes
pkill -f "runserver 8001"
pkill -f "next dev"
pkill -f "celery.*config worker"
```

## Notes

- Backend and frontend run locally for faster development
- PostgreSQL and Redis run in Docker (shared with ST environment)
- Hot reload enabled for both backend and frontend
- All AI frameworks running in MOCK mode
- Ports 8001/3001 used to avoid conflicts with Docker ST (8000/3000)
