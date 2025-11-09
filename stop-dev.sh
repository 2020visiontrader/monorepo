#!/bin/bash
# Stop local development environment

echo "Stopping development services..."

# Kill backend, frontend, and celery processes
pkill -f "runserver 8001" 2>/dev/null && echo "✓ Backend stopped" || echo "Backend not running"
pkill -f "next dev" 2>/dev/null && echo "✓ Frontend stopped" || echo "Frontend not running"
pkill -f "celery.*config worker" 2>/dev/null && echo "✓ Celery stopped" || echo "Celery not running"

echo ""
echo "Development services stopped."

