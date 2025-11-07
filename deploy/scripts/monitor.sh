#!/bin/bash
# Monitoring script with notifications
# Can be run via cron to check service health periodically

set -e

cd "$(dirname "$0")/.."

# Configuration
ALERT_EMAIL="${ALERT_EMAIL:-}"
WEBHOOK_URL="${WEBHOOK_URL:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

LOG_FILE="monitor.log"
ALERT_TRIGGERED=false

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

alert() {
    local message="$1"
    log "ALERT: $message"
    ALERT_TRIGGERED=true

    # Send email if configured
    if [ -n "$ALERT_EMAIL" ]; then
        echo "$message" | mail -s "Bot Trade Alert" "$ALERT_EMAIL" 2>/dev/null || true
    fi

    # Send webhook if configured
    if [ -n "$WEBHOOK_URL" ]; then
        curl -X POST -H 'Content-Type: application/json' \
            -d "{\"text\":\"Bot Trade Alert: $message\"}" \
            "$WEBHOOK_URL" 2>/dev/null || true
    fi
}

log "==================================="
log "Starting monitoring check..."
log "==================================="

# Check Docker
if ! docker info > /dev/null 2>&1; then
    alert "Docker is not running!"
    exit 1
fi

# Check services
SERVICES=("trading-bot" "dashboard" "nginx")
for service in "${SERVICES[@]}"; do
    if ! docker compose ps | grep -q "$service.*Up"; then
        alert "Service $service is not running!"
    else
        log "✓ Service $service is running"
    fi
done

# Check disk space
DISK_USAGE=$(df -h . | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    alert "Critical disk usage: ${DISK_USAGE}%"
elif [ "$DISK_USAGE" -gt 80 ]; then
    log "Warning: High disk usage: ${DISK_USAGE}%"
else
    log "✓ Disk usage OK: ${DISK_USAGE}%"
fi

# Check memory
MEMORY_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')
if [ "$MEMORY_USAGE" -gt 90 ]; then
    alert "Critical memory usage: ${MEMORY_USAGE}%"
elif [ "$MEMORY_USAGE" -gt 80 ]; then
    log "Warning: High memory usage: ${MEMORY_USAGE}%"
else
    log "✓ Memory usage OK: ${MEMORY_USAGE}%"
fi

# Check dashboard accessibility
if ! curl -s http://localhost:8501/_stcore/health > /dev/null 2>&1; then
    alert "Dashboard is not accessible!"
else
    log "✓ Dashboard is accessible"
fi

# Check for recent trades (if trades.csv exists)
if [ -f "../trades.csv" ]; then
    LAST_TRADE=$(tail -n 1 ../trades.csv 2>/dev/null | cut -d',' -f1)
    if [ -n "$LAST_TRADE" ]; then
        log "Last trade: $LAST_TRADE"
    fi
fi

# Check Docker logs for errors (last 5 minutes)
ERROR_COUNT=$(docker compose logs --since=5m 2>&1 | grep -i "error\|exception\|failed" | wc -l)
if [ "$ERROR_COUNT" -gt 10 ]; then
    alert "High number of errors in logs: $ERROR_COUNT"
elif [ "$ERROR_COUNT" -gt 0 ]; then
    log "Warning: Found $ERROR_COUNT errors in recent logs"
fi

log "==================================="
if [ "$ALERT_TRIGGERED" = false ]; then
    log "All checks passed!"
    exit 0
else
    log "Some checks failed - alerts sent"
    exit 1
fi
