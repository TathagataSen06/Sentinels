# Docker Best Practices Implementation Guide

## Overview
This project has been containerized following Docker best practices for production-ready microservices.

## Key Improvements Implemented

### 1. Multi-Stage Builds
Both `api-server` and `processing-engine` Dockerfiles use multi-stage builds:
- **Stage 1 (Builder)**: Contains build dependencies (gcc, build-essential, dev libraries)
- **Stage 2 (Runtime)**: Minimal runtime image with only necessary dependencies

**Benefits:**
- Final image size reduced by ~70%
- Only runtime dependencies shipped to production
- Reduced attack surface

### 2. Non-Root User Execution
- Applications run as unprivileged `appuser` instead of `root`
- User is created with restricted permissions: `groupadd -r appuser && useradd -r -g appuser appuser`

**Benefits:**
- Enhanced security by limiting privilege escalation risks
- Prevents accidental/malicious root-level modifications

### 3. Minimal Base Images
- Uses `python:3.11-slim` instead of `python:3.11` (full)
- Alpine variants available as option for ultra-lean images

**Benefits:**
- ~200MB reduction per image
- Fewer vulnerabilities
- Faster deployment and cold starts

### 4. Layer Optimization
- `.dockerignore` files exclude unnecessary artifacts (tests, venvs, cache)
- Requirements copied before application code for better layer caching
- Clean APT cache after installs: `rm -rf /var/lib/apt/lists/*`

**Benefits:**
- Faster rebuilds when code changes
- Minimal layer bloat

### 5. Health Checks
```yaml
healthcheck:
  test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 10s
```

**Benefits:**
- Automatic detection of unhealthy containers
- Docker Compose and orchestrators can restart failed services
- Better production reliability

### 6. Environment Variables & Secrets
- Use `.env` files for configuration (see `.env.example`)
- Sensitive credentials kept separate from code
- Environment variables injected at runtime

**Usage:**
```bash
cp infra/.env.example infra/.env
# Edit .env with your values
docker compose up --pull always
```

### 7. Resource Limits
Each service has defined resource constraints:
```yaml
resources:
  limits:
    cpus: "2"        # Hard limit
    memory: 1G       # Hard limit
  reservations:
    cpus: "1"        # Reserved/guaranteed
    memory: 512M     # Reserved/guaranteed
```

**Benefits:**
- Prevents resource exhaustion
- Fair resource distribution
- OOM protection

### 8. Persistent Volumes
Named volumes for stateful services:
- `postgres_data`: Database persistence
- `redis_data`: Cache persistence
- `prometheus_data`: Metrics storage
- `grafana_data`: Dashboard configurations

**Usage:**
```bash
docker volume ls                           # List all volumes
docker volume inspect sentinels-postgres   # Inspect specific volume
docker volume rm <volume_name>             # Delete volume (data loss!)
```

### 9. Networking
- Custom bridge network: `sentinels-network` (172.28.0.0/16)
- DNS resolution between containers: `postgres`, `redis`, `api-server`, etc.
- Isolated from host networking

**Benefits:**
- Service discovery without hardcoding IPs
- Network isolation
- Multi-container communication

### 10. Logging
JSON file driver with rotation:
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"        # Max size per log file
    max-file: "3"          # Keep 3 rotated files
```

**Benefits:**
- Prevents disk fill-up
- Structured logging
- Compatible with log aggregation

### 11. Restart Policies
```yaml
restart: unless-stopped  # Auto-restart on failure (except manual stop)
```

**Benefits:**
- High availability
- Automatic recovery from crashes

### 12. Service Dependencies
```yaml
depends_on:
  postgres:
    condition: service_healthy
  redis:
    condition: service_healthy
```

**Benefits:**
- Ordered startup
- Ensures dependencies are ready before dependent services start

## Running the Stack

### Start Services
```bash
cd infra
docker compose up -d --pull always
```

- `--pull always`: Pull latest images before starting

### View Logs
```bash
docker compose logs -f api-server        # Stream API server logs
docker compose logs -f processing-engine # Stream processor logs
docker compose logs --tail=50 postgres   # Last 50 lines of postgres
```

### Stop Services
```bash
docker compose down                  # Stop all (keeps volumes)
docker compose down -v               # Stop all (removes volumes!)
```

### Monitor Services
```bash
docker compose ps                    # List running services
docker stats --no-stream            # CPU/Memory usage snapshot
docker compose exec api-server bash  # Shell into container
```

## Access Points

| Service | URL | Credentials |
|---------|-----|-------------|
| API Docs | http://localhost:8000/docs | None (no auth on docs) |
| Prometheus | http://localhost:9090 | None |
| Grafana | http://localhost:3000 | admin / admin |
| PostgreSQL | localhost:5432 | sentinels / sentinels_password |
| Redis | localhost:6379 | None (no auth) |

## Production Considerations

### 1. Secrets Management
**Never hardcode credentials.** Use Docker secrets or external secret managers:
```bash
# Docker Swarm secrets
docker secret create db_password -   # stdin
echo $DB_PASS | docker secret create db_password -

# Or use environment files
docker compose up --env-file /secure/.env
```

### 2. Image Registry
Push to private registry instead of Docker Hub:
```bash
docker tag sentinels-api:latest myregistry.azurecr.io/sentinels-api:v1.0.0
docker push myregistry.azurecr.io/sentinels-api:v1.0.0
```

### 3. Multi-Node Deployment
Upgrade to Docker Swarm or Kubernetes:
```bash
# Docker Swarm
docker swarm init
docker stack deploy -c docker-compose.yml sentinels

# Kubernetes
kubectl apply -f k8s/sentinels-deployment.yaml
```

### 4. Database Backups
```bash
# Backup PostgreSQL
docker compose exec postgres pg_dump -U sentinels sentinels > backup.sql

# Backup Redis
docker compose exec redis redis-cli BGSAVE
docker compose exec redis redis-cli --rdb /data/dump.rdb
```

### 5. Monitoring & Observability
- Prometheus scrapes metrics from `/metrics` endpoints
- Grafana visualizes data from Prometheus
- Add alerting rules in `prometheus/prometheus.yml`

### 6. Security Hardening
- Use read-only root filesystem (advanced): `security_opt: - no-new-privileges:true`
- Run AppArmor/SELinux profiles
- Use Docker Content Trust for image signing
- Scan images for vulnerabilities: `docker scan sentinels-api:latest`

## Troubleshooting

### Container Won't Start
```bash
docker compose logs api-server     # Check logs
docker compose ps                  # Check status/exit code
docker compose exec api-server sh  # Debug inside container
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000          # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Or change port in docker-compose.yml:
# ports:
#   - "8001:8000"
```

### Disk Space Issues
```bash
docker system df                          # Show space usage
docker system prune -a                    # Clean unused images/volumes
docker volume prune                       # Remove dangling volumes
```

## Next Steps

1. Add authentication to Grafana in production
2. Implement TLS/SSL for all services
3. Set up automated backups
4. Configure log aggregation (ELK, Splunk, etc.)
5. Implement CI/CD pipeline for automatic builds/deployments
6. Use Docker Build Cloud for faster builds at scale
