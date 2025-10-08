# DeFi Credit Tracker - Troubleshooting Guide

## Common Issues and Solutions

### "Backend is not running" Error

This error occurs when the frontend cannot connect to the backend server. Here are the most common causes and solutions:

#### 1. Port Mismatch Issues

**Problem**: Backend and frontend are configured to use different ports.

**Solution**: 
- Backend runs on port `8001`
- Frontend runs on port `8080` (development) or `3000` (Docker)
- Frontend should connect to `http://localhost:8001` for backend API

#### 2. Backend Not Started

**Problem**: The backend server is not running.

**Solutions**:

**Option A: Use the startup scripts**
```bash
# Start both backend and frontend
./start-local.sh

# Or start them separately
./start-backend.sh    # Terminal 1
./start-frontend.sh   # Terminal 2
```

**Option B: Manual startup**
```bash
# Backend (Terminal 1)
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python production_server.py

# Frontend (Terminal 2)
cd frontend
npm install
VITE_API_BASE_URL=http://localhost:8001 npm run dev
```

**Option C: Docker Compose**
```bash
# Start all services
docker-compose up

# Or start specific services
docker-compose up backend frontend
```

#### 3. Environment Configuration Issues

**Problem**: Missing or incorrect environment variables.

**Solution**:
1. Copy the environment template:
   ```bash
   cp env.template .env
   ```
2. Update the `.env` file with your configuration
3. For local development, ensure:
   - `VITE_API_BASE_URL=http://localhost:8001` (for frontend)
   - `REDIS_URL=redis://localhost:6379` (for backend)

#### 4. CORS Issues

**Problem**: Cross-Origin Resource Sharing errors.

**Solution**: The backend is configured to allow all origins (`["*"]`), so CORS should not be an issue. If you still see CORS errors:
1. Check that the backend is running on the correct port (8001)
2. Verify the frontend is connecting to the correct URL
3. Check browser console for specific error messages

#### 5. Redis/Database Connection Issues

**Problem**: Backend cannot connect to Redis or PostgreSQL.

**Solutions**:

**For Redis**:
```bash
# Install and start Redis locally
brew install redis  # macOS
# or
sudo apt-get install redis-server  # Ubuntu

# Start Redis
redis-server
```

**For PostgreSQL (optional)**:
```bash
# Using Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=defi_password postgres:15-alpine

# Or install locally
brew install postgresql  # macOS
# or
sudo apt-get install postgresql  # Ubuntu
```

#### 6. Network/Firewall Issues

**Problem**: Ports are blocked or not accessible.

**Solution**:
1. Check if ports are in use:
   ```bash
   lsof -i :8001  # Backend port
   lsof -i :8080  # Frontend port
   ```
2. Check firewall settings
3. Try using different ports if needed

### Testing the Connection

#### 1. Test Backend Health
```bash
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "version": "2.0.0",
  "services": {
    "redis": "connected",
    "sei_services": "connected",
    "credit_scorer": "connected"
  }
}
```

#### 2. Test API Endpoint
```bash
curl "http://localhost:8001/v1/score/0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6?chain=sei"
```

#### 3. Test Frontend Connection
1. Open browser developer tools (F12)
2. Go to Network tab
3. Try to fetch a credit score
4. Check if requests are going to `http://localhost:8001`

### Docker-Specific Issues

#### 1. Service Communication
**Problem**: Services cannot communicate in Docker.

**Solution**: Use service names in Docker Compose:
- Backend: `http://backend:8001`
- Frontend: `http://frontend:80`

#### 2. Port Mapping
**Problem**: Ports not accessible from host.

**Solution**: Check `docker-compose.yml` port mappings:
```yaml
backend:
  ports:
    - "8001:8001"  # host:container

frontend:
  ports:
    - "3000:80"    # host:container
```

#### 3. Environment Variables in Docker
**Problem**: Environment variables not passed to containers.

**Solution**: Check environment section in `docker-compose.yml`:
```yaml
frontend:
  environment:
    - VITE_API_BASE_URL=http://backend:8001
```

### Development vs Production

#### Development Mode
- Backend: `http://localhost:8001`
- Frontend: `http://localhost:8080`
- Hot reload enabled
- Debug logging enabled

#### Production Mode (Docker)
- Backend: `http://backend:8001` (internal) or `http://localhost:8001` (external)
- Frontend: `http://frontend:80` (internal) or `http://localhost:3000` (external)
- No hot reload
- Optimized builds

### Logs and Debugging

#### Backend Logs
```bash
# If running manually
python production_server.py

# If running with Docker
docker-compose logs backend

# Follow logs
docker-compose logs -f backend
```

#### Frontend Logs
```bash
# If running manually
npm run dev

# If running with Docker
docker-compose logs frontend
```

#### Browser Console
1. Open browser developer tools (F12)
2. Check Console tab for JavaScript errors
3. Check Network tab for failed requests

### Quick Fixes

#### Reset Everything
```bash
# Stop all services
docker-compose down

# Remove volumes (if needed)
docker-compose down -v

# Rebuild and start
docker-compose up --build
```

#### Clear Browser Cache
1. Hard refresh (Ctrl+F5 or Cmd+Shift+R)
2. Clear browser cache
3. Try incognito/private mode

#### Check Ports
```bash
# Check what's running on ports
netstat -tulpn | grep :8001
netstat -tulpn | grep :8080

# Kill processes if needed
kill -9 <PID>
```

### Getting Help

If you're still experiencing issues:

1. Check the logs for specific error messages
2. Verify all services are running and accessible
3. Test the API endpoints directly with curl
4. Check browser console for frontend errors
5. Ensure environment variables are set correctly

### Common Error Messages

- **"Backend is not running"**: Frontend cannot reach backend
- **"Connection refused"**: Backend not started or wrong port
- **"CORS error"**: Cross-origin request blocked
- **"Network error"**: Network connectivity issue
- **"500 Internal Server Error"**: Backend error, check logs
