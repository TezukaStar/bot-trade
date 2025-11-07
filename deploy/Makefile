.PHONY: help build start stop restart logs status clean deploy update

help:
	@echo "Bot Trade - Docker Deployment Commands"
	@echo ""
	@echo "Available commands:"
	@echo "  make build      - Build Docker images"
	@echo "  make start      - Start all services"
	@echo "  make stop       - Stop all services"
	@echo "  make restart    - Restart all services"
	@echo "  make logs       - View logs (Ctrl+C to exit)"
	@echo "  make status     - Show service status"
	@echo "  make clean      - Remove containers and volumes"
	@echo "  make deploy     - Full deployment (install + build + start)"
	@echo "  make update     - Update and restart services"
	@echo "  make dev        - Start in development mode"
	@echo ""

build:
	@echo "Building Docker images..."
	docker compose build

start:
	@echo "Starting services..."
	docker compose up -d
	@echo "Dashboard available at: http://localhost:8501"

stop:
	@echo "Stopping services..."
	docker compose down

restart:
	@echo "Restarting services..."
	docker compose restart

logs:
	@echo "Viewing logs (Ctrl+C to exit)..."
	docker compose logs -f

status:
	@echo "Service status:"
	docker compose ps
	@echo ""
	@echo "Resource usage:"
	docker stats --no-stream

clean:
	@echo "Removing containers and volumes..."
	docker compose down -v
	@echo "Cleaning up Docker system..."
	docker system prune -f

deploy:
	@echo "Running full deployment..."
	./scripts/deploy.sh

update:
	@echo "Updating services..."
	./scripts/update.sh

dev:
	@echo "Starting in development mode..."
	docker compose -f docker-compose.dev.yml up

# Individual service commands
logs-bot:
	docker compose logs -f trading-bot

logs-dashboard:
	docker compose logs -f dashboard

logs-nginx:
	docker compose logs -f nginx

shell-bot:
	docker compose exec trading-bot bash

shell-dashboard:
	docker compose exec dashboard bash
