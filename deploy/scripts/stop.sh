#!/bin/bash
# Stop all services

set -e

cd "$(dirname "$0")/.."

echo "Stopping bot-trade services..."
docker compose down

echo "Services stopped successfully."
