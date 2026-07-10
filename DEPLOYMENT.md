# Deployment Guide

This guide covers deploying Intelli-Credit to various platforms and environments.

---

## Table of Contents

1. [Local Development](#local-development)
2. [Docker Deployment](#docker-deployment)
3. [Render Deployment](#render-deployment)
4. [AWS Deployment](#aws-deployment)
5. [Production Checklist](#production-checklist)
6. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- npm 9+
- PostgreSQL 15+ (optional, can use Docker)
- Redis 7+ (optional, can use Docker)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Set environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

Run the backend:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`

---

## Docker Deployment

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Vaish123-M/intelli-credit.git
cd intelli-credit

# Configure environment
cp .env.example .env
# Edit .env with your values

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Services

The docker-compose setup includes:

- **Frontend**: React app with Nginx (port 80)
- **Backend**: FastAPI application (port 8000)
- **PostgreSQL**: Database (port 5432)
- **Redis**: Cache/message broker (port 6379)
- **Prometheus**: Metrics collection (port 9090)
- **Grafana**: Metrics visualization (port 3000)

### Access Points

- Application: http://localhost
- API Documentation: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (admin/admin)

### Docker Commands

```bash
# Rebuild containers
docker-compose build

# Rebuild specific service
docker-compose build backend

# View container logs
docker-compose logs backend

# Execute command in container
docker-compose exec backend python -m pytest tests/

# Remove all volumes (WARNING: deletes data)
docker-compose down -v
```

---

## Render Deployment

### Prerequisites

- Render account (free tier available)
- GitHub repository with the code

### Steps

1. **Prepare Repository**
   - Ensure code is pushed to GitHub
   - Verify `render.yaml` exists in repository root

2. **Create PostgreSQL Database**
   - Go to Render Dashboard
   - Create new PostgreSQL instance
   - Save the connection string

3. **Create Redis Instance**
   - Create new Redis instance
   - Save the connection URL

4. **Deploy Backend**
   - Create new Web Service
   - Connect your GitHub repository
   - Set root directory to `backend`
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Add environment variables from `.env.example`
   - Deploy

5. **Deploy Frontend**
   - Create new Web Service
   - Connect your GitHub repository
   - Set root directory to `frontend`
   - Build command: `npm run build`
   - Start command: `npm run preview`
   - Add environment variable for API URL
   - Deploy

### Environment Variables for Render

Add these in Render dashboard:

```
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=your-secret-key
NEWS_API_KEY=your-news-api-key
SERPAPI_KEY=your-serpapi-key
GOOGLE_API_KEY=your-google-api-key
GOOGLE_CSE_ID=your-google-cse-id
ANTHROPIC_API_KEY=your-anthropic-api-key
OPENAI_API_KEY=your-openai-api-key
HIGH_RISK_THRESHOLD=0.6
CORS_ORIGINS=https://your-frontend-url.onrender.com
```

---

## AWS Deployment

### Using ECS (Elastic Container Service)

#### 1. Push Docker Images to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Create repository
aws ecr create-repository --repository-name intelli-credit-backend

# Tag and push backend
docker tag intelli-credit-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/intelli-credit-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/intelli-credit-backend:latest
```

#### 2. Create ECS Cluster

```bash
aws ecs create-cluster --cluster-name intelli-credit
```

#### 3. Create Task Definition

Create a task definition file `task-definition.json`:

```json
{
  "family": "intelli-credit-backend",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/intelli-credit-backend:latest",
      "memory": 512,
      "cpu": 256,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "DATABASE_URL",
          "value": "postgresql://..."
        }
      ]
    }
  ]
}
```

Register task definition:
```bash
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### 4. Create Service

```bash
aws ecs create-service \
  --cluster intelli-credit \
  --service-name backend-service \
  --task-definition intelli-credit-backend \
  --desired-count 1 \
  --launch-type FARGATE
```

#### 5. Configure Load Balancer

```bash
# Create load balancer
aws elbv2 create-load-balancer \
  --name intelli-credit-lb \
  --subnets subnet-123 subnet-456 \
  --security-groups sg-123

# Create target group
aws elbv2 create-target-group \
  --name backend-targets \
  --port 8000 \
  --protocol HTTP \
  --vpc-id vpc-123

# Register targets
aws elbv2 register-targets \
  --target-group-arn <target-group-arn> \
  --targets Id=<instance-id>
```

### Using AWS App Runner (Simpler)

1. Create ECR repository and push images (same as above)
2. Go to AWS App Runner console
3. Create new service
4. Select source: ECR image
5. Configure environment variables
6. Deploy

---

## Production Checklist

### Security

- [ ] Change `SECRET_KEY` to a strong random string (32+ characters)
- [ ] Enable HTTPS/TLS for all endpoints
- [ ] Configure CORS to specific origins only
- [ ] Set up firewall rules
- [ ] Enable database SSL connections
- [ ] Rotate API keys regularly
- [ ] Enable security headers (CSP, HSTS, X-Frame-Options)

### Database

- [ ] Use managed PostgreSQL service (RDS, Neon, Supabase)
- [ ] Enable automated backups
- [ ] Configure read replicas for scaling
- [ ] Set up connection pooling
- [ ] Enable query logging for monitoring
- [ ] Create migration rollback plan

### Performance

- [ ] Enable Redis caching
- [ ] Configure CDN for static assets
- [ ] Enable gzip compression
- [ ] Set up database indexes
- [ ] Configure connection pooling
- [ ] Enable response caching where appropriate

### Monitoring

- [ ] Set up Prometheus metrics collection
- [ ] Configure Grafana dashboards
- [ ] Set up alerting rules
- [ ] Enable error tracking (Sentry)
- [ ] Configure log aggregation (ELK, CloudWatch)
- [ ] Set up uptime monitoring

### Reliability

- [ ] Configure health checks
- [ ] Set up auto-scaling
- [ ] Implement retry logic for external APIs
- [ ] Configure circuit breakers
- [ ] Set up graceful shutdown
- [ ] Implement database failover

### Compliance

- [ ] Enable audit logging
- [ ] Implement data retention policies
- [ ] Set up GDPR compliance if needed
- [ ] Document data flow
- [ ] Implement access logging
- [ ] Regular security audits

---

## Troubleshooting

### Backend won't start

**Issue**: Port already in use
```bash
# Check what's using port 8000
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Kill the process
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows
```

**Issue**: Database connection failed
```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check logs
docker-compose logs postgres

# Test connection
psql -h localhost -U intelli_user -d intelli_credit
```

### Frontend build fails

**Issue**: Module not found
```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Issue**: API connection refused
```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Verify VITE_API_BASE_URL is set correctly
```

### Docker issues

**Issue**: Container won't start
```bash
# Check container logs
docker-compose logs <service-name>

# Rebuild without cache
docker-compose build --no-cache

# Check disk space
df -h
```

**Issue**: Volume permission errors
```bash
# Fix permissions on Linux
sudo chown -R $USER:$USER ./backend/data
sudo chown -R $USER:$USER ./backend/uploads
```

### Rate limiting errors

**Issue**: 429 Too Many Requests
```bash
# Check rate limit configuration
# Adjust limits in .env
RATE_LIMIT_PER_MINUTE=200

# Or temporarily disable for testing
RATE_LIMIT_ENABLED=False
```

### Authentication issues

**Issue**: Token expired
```bash
# Token expires after 30 minutes by default
# Re-login to get a new token
# Adjust ACCESS_TOKEN_EXPIRE_MINUTES in code if needed
```

**Issue**: Invalid credentials
```bash
# Verify password hashing
# Check user exists in database
# Ensure JWT secret key matches
```

---

## Performance Tuning

### Backend

```python
# In main.py, adjust worker count
# For production, use gunicorn with multiple workers
# gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Database

```sql
-- Add indexes for common queries
CREATE INDEX idx_deals_company ON deals(company_name);
CREATE INDEX idx_deals_risk ON deals(risk_score);
CREATE INDEX idx_entities_created ON entities(created_at);
```

### Redis

```bash
# Configure Redis memory limits
# In redis.conf:
maxmemory 256mb
maxmemory-policy allkeys-lru
```

---

## Backup and Recovery

### Database Backup

```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U intelli_user intelli_credit > backup.sql

# Restore
docker-compose exec -T postgres psql -U intelli_user intelli_credit < backup.sql
```

### File Backup

```bash
# Backup uploads and downloads
tar -czf backups/uploads-$(date +%Y%m%d).tar.gz backend/uploads/
tar -czf backups/downloads-$(date +%Y%m%d).tar.gz backend/downloads/
```

### State Backup

```bash
# Backup application state
cp backend/data/app_state.json backups/state-$(date +%Y%m%d).json
```

---

## Scaling Strategies

### Horizontal Scaling

- Use load balancer (Nginx, AWS ALB)
- Deploy multiple backend instances
- Use Redis for session sharing
- Implement database read replicas

### Vertical Scaling

- Increase CPU/memory allocation
- Optimize database queries
- Enable connection pooling
- Use caching aggressively

### Cost Optimization

- Use spot instances for non-critical workloads
- Implement auto-scaling
- Optimize Docker image sizes
- Use CDN for static assets
- Compress database backups

---

## Support

For issues or questions:
- Check the main README.md
- Review API documentation at `/docs`
- Check logs in Docker: `docker-compose logs -f`
- Open an issue on GitHub
