#!/bin/bash
# Update and restart services

set -e

cd "$(dirname "$0")/.."

echo "Pulling latest code..."
cd ..
git pull

echo "Rebuilding Docker images..."
cd deploy
docker compose build

echo "Restarting services..."
docker compose down
docker compose up -d

echo "Waiting for services to be ready..."
sleep 5

echo "Service status:"
docker compose ps

echo ""
echo "Update completed successfully!"
echo "Dashboard available at: http://localhost:8501"
