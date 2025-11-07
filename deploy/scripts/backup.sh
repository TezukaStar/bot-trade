#!/bin/bash
# Backup script for trade data and configurations

set -e

DEPLOY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="$DEPLOY_DIR/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="bot-trade-backup-$DATE.tar.gz"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "==================================="
echo "Bot Trade - Backup Script"
echo "==================================="
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo -e "${GREEN}Creating backup: $BACKUP_FILE${NC}"
echo ""

# Backup configuration files
echo "Backing up configuration files..."
tar -czf "/tmp/config-backup.tar.gz" \
    -C "$DEPLOY_DIR" \
    .env \
    docker-compose.yml \
    nginx/ \
    2>/dev/null || echo -e "${YELLOW}Warning: Some config files not found${NC}"

# Backup trade data from Docker volume
echo "Backing up trade data..."
docker run --rm \
    -v deploy_trades-data:/data \
    -v "$BACKUP_DIR:/backup" \
    ubuntu tar czf "/backup/trades-data-$DATE.tar.gz" /data \
    2>/dev/null || echo -e "${YELLOW}Warning: Could not backup trade data${NC}"

# Backup versions directory
echo "Backing up strategy versions..."
tar -czf "/tmp/versions-backup.tar.gz" \
    -C "$DEPLOY_DIR/.." \
    versions/ \
    2>/dev/null || echo -e "${YELLOW}Warning: Could not backup versions${NC}"

# Combine all backups
echo "Creating combined backup archive..."
cd /tmp
tar -czf "$BACKUP_DIR/$BACKUP_FILE" \
    config-backup.tar.gz \
    versions-backup.tar.gz \
    2>/dev/null || true

# Cleanup temp files
rm -f /tmp/config-backup.tar.gz /tmp/versions-backup.tar.gz

echo ""
echo -e "${GREEN}Backup completed: $BACKUP_DIR/$BACKUP_FILE${NC}"
echo ""

# List backups
echo "Available backups:"
ls -lh "$BACKUP_DIR"

echo ""

# Cleanup old backups (keep last 7 days)
echo "Cleaning up old backups (keeping last 7 days)..."
find "$BACKUP_DIR" -name "bot-trade-backup-*.tar.gz" -mtime +7 -delete
find "$BACKUP_DIR" -name "trades-data-*.tar.gz" -mtime +7 -delete

echo ""
echo -e "${GREEN}Backup process completed!${NC}"
