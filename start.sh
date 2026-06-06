#!/bin/bash
# Quick-start script for Sentinels Docker deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Sentinels Docker Quick Start        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose are installed${NC}"

# Navigate to infra directory
cd "$(dirname "$0")/infra"

# Create .env if not exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}→ Creating .env file from .env.example${NC}"
    cp .env.example .env
    echo -e "${GREEN}✓ .env created (adjust values if needed)${NC}"
fi

# Pull latest images
echo -e "${YELLOW}→ Pulling latest images...${NC}"
docker compose pull

# Build local images
echo -e "${YELLOW}→ Building Docker images...${NC}"
docker compose build

# Start services
echo -e "${YELLOW}→ Starting services...${NC}"
docker compose up -d --wait

# Check service health
echo -e "${YELLOW}→ Verifying services...${NC}"
sleep 5

if docker compose ps | grep -q "healthy"; then
    echo -e "${GREEN}✓ Services are healthy${NC}"
else
    echo -e "${YELLOW}⚠ Some services may still be starting...${NC}"
    docker compose ps
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Deployment Complete!               ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo "Access Points:"
echo -e "  ${YELLOW}API Docs${NC}:      http://localhost:8000/docs"
echo -e "  ${YELLOW}Grafana${NC}:       http://localhost:3000 (admin/admin)"
echo -e "  ${YELLOW}Prometheus${NC}:    http://localhost:9090"
echo -e "  ${YELLOW}PostgreSQL${NC}:    localhost:5432"
echo -e "  ${YELLOW}Redis${NC}:         localhost:6379"
echo ""
echo "Common Commands:"
echo "  View logs:     docker compose logs -f <service_name>"
echo "  Stop all:      docker compose down"
echo "  Status:        docker compose ps"
echo "  Shell access:  docker compose exec <service> bash"
echo ""
