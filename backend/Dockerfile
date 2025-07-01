# syntax=docker/dockerfile:1

############################
# Stage 1: Build dependencies
############################
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy and install only requirements first for better caching
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

############################
# Stage 2: Copy app code
############################
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app
COPY scripts/seed.py ./scripts/seed.py

# Expose the port FastAPI will run on
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Run migrations or seed if needed (optional)
# Uncomment to run seed at container start:
# ENTRYPOINT ["python", "scripts/seed.py", "&&"]

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


Multi-stage build

builder installs system packages and Python deps.

Final image copies only the necessary wheel/env files for a slimmer runtime.

requirements.txt is used to cache dependencies.

Copy app code into /app/app, matching your backend/app folder.

Expose port 8000 for Uvicorn.

CMD starts FastAPI via Uvicorn.

bash 
cd medassistant/backend
docker build -t medassistant-backend:latest .
docker run --rm -p 8000:8000 medassistant-backend:latest
And integrate it into your docker-compose.yml or CI workflows.