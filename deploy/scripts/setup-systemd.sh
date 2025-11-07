#!/bin/bash
# Setup systemd services for bot-trade

set -e

DEPLOY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SYSTEMD_DIR="$DEPLOY_DIR/systemd"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "==================================="
echo "Bot Trade - Systemd Setup"
echo "==================================="
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Please run with sudo:${NC}"
    echo "sudo $0"
    exit 1
fi

# Get the actual user (not root)
ACTUAL_USER=${SUDO_USER:-$USER}
ACTUAL_HOME=$(eval echo ~$ACTUAL_USER)

echo -e "${GREEN}Step 1: Creating log directory...${NC}"
mkdir -p /var/log/bot-trade
chown -R $ACTUAL_USER:$ACTUAL_USER /var/log/bot-trade

echo -e "${GREEN}Step 2: Updating service files with correct paths...${NC}"

# Update service files with actual paths and user
for file in "$SYSTEMD_DIR"/*.service "$SYSTEMD_DIR"/*.timer; do
    if [ -f "$file" ]; then
        sed -e "s|YOUR_USERNAME|$ACTUAL_USER|g" \
            -e "s|/path/to/bot-trade|$DEPLOY_DIR/..|g" \
            "$file" > "/tmp/$(basename $file)"
    fi
done

echo -e "${GREEN}Step 3: Installing service files...${NC}"

# Copy service files to systemd directory
cp /tmp/bot-trade.service /etc/systemd/system/
cp /tmp/bot-trade.timer /etc/systemd/system/
cp /tmp/bot-trade-dashboard.service /etc/systemd/system/

# Cleanup temp files
rm -f /tmp/bot-trade*.service /tmp/bot-trade*.timer

echo -e "${GREEN}Step 4: Reloading systemd daemon...${NC}"
systemctl daemon-reload

echo ""
echo "==================================="
echo "Installation completed!"
echo "==================================="
echo ""

echo "Available services:"
echo ""
echo "1. Trading Bot (scheduled):"
echo "   sudo systemctl enable bot-trade.timer"
echo "   sudo systemctl start bot-trade.timer"
echo ""
echo "2. Dashboard (always running):"
echo "   sudo systemctl enable bot-trade-dashboard"
echo "   sudo systemctl start bot-trade-dashboard"
echo ""

read -p "Do you want to enable and start these services now? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${GREEN}Enabling and starting services...${NC}"

    # Enable and start timer for trading bot
    systemctl enable bot-trade.timer
    systemctl start bot-trade.timer

    # Enable and start dashboard
    systemctl enable bot-trade-dashboard
    systemctl start bot-trade-dashboard

    echo ""
    echo -e "${GREEN}Services started successfully!${NC}"
    echo ""

    # Show status
    echo "Timer status:"
    systemctl status bot-trade.timer --no-pager
    echo ""

    echo "Dashboard status:"
    systemctl status bot-trade-dashboard --no-pager
    echo ""

    echo "Next scheduled runs:"
    systemctl list-timers bot-trade.timer --no-pager
else
    echo "Services installed but not started."
    echo "You can start them manually later."
fi

echo ""
echo "Useful commands:"
echo "  sudo systemctl status bot-trade.timer"
echo "  sudo systemctl status bot-trade-dashboard"
echo "  sudo journalctl -u bot-trade -f"
echo "  sudo journalctl -u bot-trade-dashboard -f"
echo "  sudo systemctl list-timers"
echo ""
