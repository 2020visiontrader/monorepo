#!/bin/bash
# Start local development environment

set -e

echo "=== Starting Local Development Environment ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker services are running
echo -e "${YELLOW}Checking Docker services (PostgreSQL, Redis)...${NC}"
cd ops
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo "Starting Docker services..."
    docker-compose up -d postgres redis
    echo "Waiting for services to be healthy..."
    sleep 5
else
    echo -e "${GREEN}✓ Docker services are running${NC}"
fi
cd ..

# Start backend
echo ""
echo -e "${YELLOW}Starting backend dev server on port 8001...${NC}"
cd backend
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << 'EOF'
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
EOF
fi

echo "Running migrations..."
poetry run python manage.py migrate > /dev/null 2>&1 || true

echo "Starting backend server..."
poetry run python manage.py runserver 8001 &
BACKEND_PID=$!
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID) on http://localhost:8001${NC}"
cd ..

# Start frontend
echo ""
echo -e "${YELLOW}Starting frontend dev server on port 3001...${NC}"
cd frontend
if [ ! -f .env.local ]; then
    echo "Creating .env.local file..."
    echo "NEXT_PUBLIC_API_URL=http://localhost:8001" > .env.local
    echo "NEXT_PUBLIC_ENV=ST" >> .env.local
fi

echo "Starting frontend server..."
PORT=3001 pnpm dev &
FRONTEND_PID=$!
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID) on http://localhost:3001${NC}"
cd ..

# Start Celery worker
echo ""
echo -e "${YELLOW}Starting Celery worker...${NC}"
cd backend
poetry run celery -A config worker -l info &
CELERY_PID=$!
echo -e "${GREEN}✓ Celery worker started (PID: $CELERY_PID)${NC}"
cd ..

echo ""
echo -e "${GREEN}=== Development Environment Started ===${NC}"
echo ""
echo "Services:"
echo "  - Backend:  http://localhost:8001"
echo "  - Frontend: http://localhost:3001"
echo "  - Admin:    http://localhost:8001/admin"
echo ""
echo "Process IDs:"
echo "  - Backend:  $BACKEND_PID"
echo "  - Frontend: $FRONTEND_PID"
echo "  - Celery:   $CELERY_PID"
echo ""
echo "To stop services, run:"
echo "  kill $BACKEND_PID $FRONTEND_PID $CELERY_PID"
echo ""
echo "Or use: ./stop-dev.sh"
echo ""

# Wait for user interrupt
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID $CELERY_PID 2>/dev/null; exit" INT TERM

echo "Press Ctrl+C to stop all services"
wait

