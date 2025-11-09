# Local Development Environment Setup

## Quick Start

### Option 1: Using Startup Script (Recommended)

```bash
# Start all dev services
./start-dev.sh

# Stop all dev services (in another terminal)
./stop-dev.sh
```

### Option 2: Manual Startup (Separate Terminals)

#### Terminal 1: Backend
```bash
cd backend
poetry run python manage.py runserver 8001
```

#### Terminal 2: Frontend
```bash
cd frontend
PORT=3001 pnpm dev
```

#### Terminal 3: Celery Worker
```bash
cd backend
poetry run celery -A config worker -l info
```

## Prerequisites

1. **Docker Compose** - For PostgreSQL and Redis
   ```bash
   # Start infrastructure services
   cd ops
   docker-compose up -d postgres redis
   ```

2. **Poetry** - For Python dependencies
   ```bash
   pip install poetry
   cd backend
   poetry install --no-root
   ```

3. **pnpm** - For Node.js dependencies
   ```bash
   npm install -g pnpm
   cd frontend
   pnpm install
   ```

## Configuration

### Backend (.env)
Located in `backend/.env`:
```env
ENVIRONMENT=ST
DEBUG=True
DB_NAME=ecommerce_optimizer
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/1
SECRET_KEY=django-insecure-dev-key-change-in-production
ROUTELLM_API_KEY=
```

### Frontend (.env.local)
Located in `frontend/.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_ENV=ST
```

## Access URLs

- **Frontend:** http://localhost:3001
- **Backend API:** http://localhost:8001
- **Admin Panel:** http://localhost:8001/admin

## Demo Credentials

- **Email:** admin@demo.com
- **Password:** password123!

## Database Setup

Migrations are run automatically on startup. To run manually:

```bash
cd backend
poetry run python manage.py migrate
```

To seed demo data:

```bash
cd backend
poetry run python manage.py shell
# Then run the seed script from Django shell
```

## Troubleshooting

### Port Conflicts
- Backend uses port **8001** (to avoid conflict with Docker ST on 8000)
- Frontend uses port **3001** (to avoid conflict with Docker ST on 3000)
- If ports are still in use, check with: `lsof -i :8001` or `lsof -i :3001`

### Database Connection Issues
- Ensure Docker PostgreSQL is running: `docker-compose ps` (in ops directory)
- Check connection: `psql -h localhost -U postgres -d ecommerce_optimizer`

### Redis Connection Issues
- Ensure Docker Redis is running: `docker-compose ps` (in ops directory)
- Check connection: `redis-cli ping`

### Process Management
```bash
# Find processes
ps aux | grep -E "(runserver|next|celery)"

# Kill processes
pkill -f "runserver 8001"
pkill -f "next dev"
pkill -f "celery.*config worker"
```

## Development Workflow

1. **Start Docker infrastructure** (if not already running):
   ```bash
   cd ops && docker-compose up -d postgres redis
   ```

2. **Start development servers**:
   ```bash
   ./start-dev.sh
   # Or start manually in separate terminals
   ```

3. **Make changes** - Both backend and frontend have hot reload enabled

4. **View logs**:
   - Backend: Check terminal output
   - Frontend: Check terminal output
   - Celery: Check terminal output

5. **Stop services**:
   ```bash
   ./stop-dev.sh
   # Or Ctrl+C in each terminal
   ```

## Notes

- Backend and frontend run locally for faster development
- PostgreSQL and Redis run in Docker (shared with ST environment)
- Hot reload is enabled for both backend and frontend
- All AI frameworks run in MOCK mode (no API keys needed)
- Ports 8001/3001 are used to avoid conflicts with Docker ST (8000/3000)
