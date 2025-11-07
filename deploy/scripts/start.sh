#!/bin/bash
# Start all services

set -e

cd "$(dirname "$0")/.."

echo "Starting bot-trade services..."
docker compose up -d

echo "Waiting for services to be ready..."
sleep 5

echo "Service status:"
docker compose ps

echo ""
echo "Dashboard available at: http://localhost:8501"
echo "View logs: docker compose logs -f"
