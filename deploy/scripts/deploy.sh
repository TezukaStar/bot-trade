#!/bin/bash
# Deployment script for bot-trade on Ubuntu with Docker

set -e

echo "==================================="
echo "Bot Trade - Deployment Script"
echo "==================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on Ubuntu
if [ ! -f /etc/os-release ]; then
    echo -e "${RED}Error: Cannot detect OS${NC}"
    exit 1
fi

. /etc/os-release
if [[ "$ID" != "ubuntu" ]]; then
    echo -e "${YELLOW}Warning: This script is designed for Ubuntu. Detected: $ID${NC}"
fi

echo -e "${GREEN}Step 1: Checking prerequisites...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker not found. Installing Docker...${NC}"

    # Update package index
    sudo apt-get update

    # Install prerequisites
    sudo apt-get install -y \
        ca-certificates \
        curl \
        gnupg \
        lsb-release

    # Add Docker's official GPG key
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker Engine
    sudo apt-get update
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

    # Add current user to docker group
    sudo usermod -aG docker $USER

    echo -e "${GREEN}Docker installed successfully!${NC}"
    echo -e "${YELLOW}Please log out and log back in for group changes to take effect.${NC}"
else
    echo -e "${GREEN}Docker is already installed.${NC}"
fi

# Check Docker Compose
if ! docker compose version &> /dev/null; then
    echo -e "${RED}Error: Docker Compose plugin not found${NC}"
    exit 1
else
    echo -e "${GREEN}Docker Compose is available.${NC}"
fi

echo -e "${GREEN}Step 2: Setting up environment...${NC}"

# Navigate to deploy directory
cd "$(dirname "$0")/.."

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}.env file not found. Copying from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}IMPORTANT: Please edit .env file with your credentials!${NC}"
    echo -e "${YELLOW}Run: nano .env${NC}"
    read -p "Press Enter after you've configured .env file..."
fi

echo -e "${GREEN}Step 3: Building Docker images...${NC}"
docker compose build

echo -e "${GREEN}Step 4: Starting services...${NC}"
docker compose up -d

echo -e "${GREEN}Step 5: Checking service status...${NC}"
sleep 5
docker compose ps

echo ""
echo -e "${GREEN}==================================="
echo "Deployment completed successfully!"
echo "===================================${NC}"
echo ""
echo "Access the dashboard at: http://localhost:8501"
echo ""
echo "Useful commands:"
echo "  - View logs:        docker compose logs -f"
echo "  - Stop services:    docker compose down"
echo "  - Restart services: docker compose restart"
echo "  - View status:      docker compose ps"
echo ""
