#!/bin/bash
# View logs from services

cd "$(dirname "$0")/.."

SERVICE=${1:-}

if [ -z "$SERVICE" ]; then
    echo "Viewing logs from all services (Ctrl+C to exit)..."
    docker compose logs -f
else
    echo "Viewing logs from $SERVICE (Ctrl+C to exit)..."
    docker compose logs -f "$SERVICE"
fi
