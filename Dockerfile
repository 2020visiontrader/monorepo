FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY backend/pyproject.toml ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && (poetry install --no-dev --no-root || poetry install --without dev --no-root)

# Copy application code
COPY . .

# Collect static files (only for web services, skip for workers)
# RUN cd backend && python manage.py collectstatic --noinput || true

# Expose port (only for web services)
# EXPOSE 8000

# No CMD - workers use startCommand from render.yaml
