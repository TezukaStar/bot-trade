#!/bin/bash
# Health check script for monitoring services

set -e

cd "$(dirname "$0")/.."

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "==================================="
echo "Bot Trade - Health Check"
echo "==================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
else
    echo -e "${GREEN}✓ Docker is running${NC}"
fi

# Check if services are up
SERVICES=("trading-bot" "dashboard" "nginx")
ALL_HEALTHY=true

for service in "${SERVICES[@]}"; do
    if docker compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✓ $service is running${NC}"

        # Check container health
        HEALTH=$(docker inspect --format='{{.State.Health.Status}}' "bot-trade-$service" 2>/dev/null || echo "none")
        if [ "$HEALTH" != "none" ]; then
            if [ "$HEALTH" == "healthy" ]; then
                echo -e "  ${GREEN}Health: $HEALTH${NC}"
            else
                echo -e "  ${YELLOW}Health: $HEALTH${NC}"
            fi
        fi
    else
        echo -e "${RED}✗ $service is not running${NC}"
        ALL_HEALTHY=false
    fi
done

echo ""

# Check if dashboard is accessible
if curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Dashboard is accessible at http://localhost:8501${NC}"
else
    echo -e "${YELLOW}⚠ Dashboard health check failed${NC}"
    ALL_HEALTHY=false
fi

echo ""

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    echo -e "${RED}✗ Disk usage is critical: ${DISK_USAGE}%${NC}"
    ALL_HEALTHY=false
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo -e "${YELLOW}⚠ Disk usage is high: ${DISK_USAGE}%${NC}"
else
    echo -e "${GREEN}✓ Disk usage is OK: ${DISK_USAGE}%${NC}"
fi

# Check memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEMORY_USAGE" -gt 90 ]; then
    echo -e "${RED}✗ Memory usage is critical: ${MEMORY_USAGE}%${NC}"
    ALL_HEALTHY=false
elif [ "$MEMORY_USAGE" -gt 80 ]; then
    echo -e "${YELLOW}⚠ Memory usage is high: ${MEMORY_USAGE}%${NC}"
else
    echo -e "${GREEN}✓ Memory usage is OK: ${MEMORY_USAGE}%${NC}"
fi

echo ""
echo "==================================="

if [ "$ALL_HEALTHY" = true ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some checks failed${NC}"
    exit 1
fi
