#!/bin/bash
# Check status of all services

cd "$(dirname "$0")/.."

echo "==================================="
echo "Bot Trade - Service Status"
echo "==================================="
echo ""

docker compose ps

echo ""
echo "Resource usage:"
docker stats --no-stream

echo ""
echo "Recent logs (last 20 lines):"
docker compose logs --tail=20
