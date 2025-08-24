# Multi-stage build for single container deployment
# Note: Frontend should be built locally first to avoid architecture issues
# Run: cd frontend && npm install && npm run build

# Python backend stage
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including nginx
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    nginx \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY backend/ .

# Copy built frontend (built locally)
COPY frontend/dist /var/www/html

# Create nginx configuration for single container
RUN echo 'server { \
    listen 80; \
    server_name localhost; \
    \
    # Serve static frontend files \
    location / { \
        root /var/www/html; \
        try_files $uri $uri/ /index.html; \
        add_header Cache-Control "no-cache, no-store, must-revalidate"; \
    } \
    \
    # Proxy API requests to backend \
    location /api/ { \
        proxy_pass http://localhost:8000/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # Proxy v1 API requests to backend \
    location /v1/ { \
        proxy_pass http://localhost:8000/v1/; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for; \
        proxy_set_header X-Forwarded-Proto $scheme; \
    } \
    \
    # Health check endpoint \
    location /health { \
        proxy_pass http://localhost:8000/health; \
        proxy_set_header Host $host; \
    } \
    \
    # API documentation \
    location /docs { \
        proxy_pass http://localhost:8000/docs; \
        proxy_set_header Host $host; \
    } \
}' > /etc/nginx/sites-available/default

# Create startup script
RUN echo '#!/bin/bash \n\
# Start nginx in background \n\
nginx \n\
\n\
# Start the FastAPI backend \n\
cd /app \n\
uvicorn production_server:app --host 0.0.0.0 --port 8000 --workers 1 \n\
' > /start.sh && chmod +x /start.sh

# Create non-root user
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app /var/www/html

# Expose port 80 for nginx
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Start both services
CMD ["/start.sh"]
