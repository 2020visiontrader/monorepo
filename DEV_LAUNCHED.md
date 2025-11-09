# Development Environment - Launched

## Services Running

### Backend
- **URL:** http://localhost:8001
- **Admin:** http://localhost:8001/admin
- **Status:** Running
- **Logs:** `/tmp/backend-dev.log`

### Frontend  
- **URL:** http://localhost:3001
- **Status:** Running
- **Logs:** `/tmp/frontend-dev.log`

### Celery Worker
- **Status:** Running
- **Logs:** `/tmp/celery-dev.log`

## Quick Access

- **Frontend:** http://localhost:3001
- **Backend API:** http://localhost:8001
- **Admin Panel:** http://localhost:8001/admin

## Demo Credentials

- **Email:** admin@demo.com
- **Password:** password123!

## View Logs

```bash
# Backend logs
tail -f /tmp/backend-dev.log

# Frontend logs
tail -f /tmp/frontend-dev.log

# Celery logs
tail -f /tmp/celery-dev.log
```

## Stop Services

```bash
# Find and stop processes
pkill -f "runserver 8001"
pkill -f "next dev"
pkill -f "celery.*config worker"

# Or use the stop script
./stop-dev.sh
```

## Notes

- Services are running in the background
- Hot reload is enabled for both backend and frontend
- Database and Redis are provided by Docker (ports 5432, 6379)
- All AI frameworks are in MOCK mode (safe for testing)
