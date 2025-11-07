#!/bin/bash
# Setup cron jobs for automated trading

set -e

DEPLOY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPT_DIR="$DEPLOY_DIR/scripts"

echo "==================================="
echo "Bot Trade - Cron Setup"
echo "==================================="

# Create run-bot.sh script for cron
cat > "$SCRIPT_DIR/run-bot.sh" << 'EOF'
#!/bin/bash
# Script to run trading bot via cron

DEPLOY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$DEPLOY_DIR"

# Run the bot container
docker compose run --rm trading-bot

# Log the execution
echo "$(date): Trading bot executed" >> "$DEPLOY_DIR/cron.log"
EOF

chmod +x "$SCRIPT_DIR/run-bot.sh"

# Create crontab entries
CRON_FILE="/tmp/bot-trade-cron"

cat > "$CRON_FILE" << EOF
# Bot Trade - Automated Trading Schedule
# Runs during premium sessions (high win rate)

# PUT Session: 12:00-13:59 UTC (every 30 minutes)
0,30 12-13 * * * $SCRIPT_DIR/run-bot.sh >> $DEPLOY_DIR/cron.log 2>&1

# CALL Session: 18:00-18:59 UTC (every 30 minutes)
0,30 18 * * * $SCRIPT_DIR/run-bot.sh >> $DEPLOY_DIR/cron.log 2>&1

# Optional: Daily cleanup of old logs (keep last 7 days)
0 0 * * * find $DEPLOY_DIR -name "*.log" -mtime +7 -delete

EOF

# Show the cron entries
echo ""
echo "Proposed cron schedule:"
echo "======================="
cat "$CRON_FILE"
echo "======================="
echo ""

# Ask for confirmation
read -p "Do you want to install these cron jobs? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup existing crontab
    crontab -l > /tmp/crontab-backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

    # Add new cron jobs (append to existing)
    (crontab -l 2>/dev/null; cat "$CRON_FILE") | crontab -

    echo "Cron jobs installed successfully!"
    echo ""
    echo "Current crontab:"
    crontab -l
    echo ""
    echo "Logs will be written to: $DEPLOY_DIR/cron.log"
else
    echo "Cron installation cancelled."
fi

rm -f "$CRON_FILE"
