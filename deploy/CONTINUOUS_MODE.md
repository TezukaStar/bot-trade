# Bot Trade - Continuous Mode Guide

## 🔄 Running in Continuous Mode (24/7)

The bot now supports **continuous mode** which runs 24/7 and automatically checks for trading signals every 30 seconds.

---

## ✨ Key Features

### Continuous Mode (Default for Docker)
- ✅ Runs 24/7 without stopping
- ✅ Checks signals every 30 seconds
- ✅ Auto-restarts if crashed (Docker `restart: always`)
- ✅ Graceful shutdown on SIGTERM/SIGINT
- ✅ Trades only during configured sessions (respects `trading_hours` and `session_filters`)
- ✅ Perfect for dedicated servers/VPS

### Scheduled Mode (GitHub Actions)
- ✅ Runs for 11 minutes per execution
- ✅ Designed for GitHub Actions free tier
- ✅ Same trading logic as continuous mode

---

## 🚀 Usage

### Docker Deployment (Recommended for 24/7)

The default `docker-compose.yml` runs in continuous mode:

```bash
cd bot-trade/deploy

# Start services
./scripts/start.sh

# Bot will run continuously, checking signals every 30s
```

**What happens:**
- Trading bot runs 24/7 in a Docker container
- Automatically checks all enabled pairs every 30 seconds
- Only trades when conditions match (session filters + indicators)
- Auto-restarts if it crashes

### Manual Run (Continuous Mode)

```bash
# With Python directly
python bot_v1.4.py --continuous

# With Docker
docker compose up trading-bot

# In background
docker compose up -d trading-bot
```

### Manual Run (Scheduled Mode)

```bash
# Run for 11 minutes then exit
python bot_v1.4.py

# Or explicitly
python bot_v1.4.py --scheduled
```

---

## 🛑 Stopping the Bot

### Graceful Shutdown

```bash
# Stop Docker services
./scripts/stop.sh

# Or directly
docker compose down
```

The bot will:
1. Receive SIGTERM signal
2. Finish current trade check
3. Save any pending data
4. Exit cleanly

### Force Stop (Not Recommended)

```bash
docker compose kill trading-bot
```

---

## 📊 Monitoring

### View Live Logs

```bash
# All logs
./scripts/logs.sh

# Just trading bot
docker compose logs -f trading-bot
```

### Check Status

```bash
./scripts/status.sh
```

### Expected Output (Continuous Mode)

```
🤖 Trade Bot V1.4 Starting (CONTINUOUS MODE)
✅ Enabled pairs: EURUSD, EURUSD-OTC, EURCAD
⏰ Start time: 2025-11-07 12:00:00 UTC
🔄 Continuous monitoring: checking signals every 30 seconds
♾️  Running 24/7 until stopped (Ctrl+C or SIGTERM)

============================================================
🔄 Iteration #1 - 2025-11-07 12:00:00 UTC (Uptime: 0h 0m)
============================================================

🔍 Checking EURUSD...
⏭️  No signal for EURUSD (outside session filter)

🔍 Checking EURUSD-OTC...
🔔 Signal detected: PUT
✅ Trade #1 executed successfully

💤 Waiting 30s before next check...
```

---

## ⚙️ Configuration

The bot respects your `versions/v1.4/config.json` settings:

### Trading Hours
```json
"trading_hours": {
  "start": 19,  // Start hour (UTC)
  "end": 3      // End hour (UTC)
}
```

### Session Filters
```json
"session_filters": {
  "19-21": "put",   // Only PUT trades 19:00-21:00
  "22-2": "call"    // Only CALL trades 22:00-02:00
}
```

**The bot checks these conditions continuously but only trades when ALL conditions are met:**
1. ✅ Within trading_hours
2. ✅ Within session_filter
3. ✅ Indicators pass (ADX, MACD, EMA, Slope)

---

## 🔄 Comparison: Continuous vs Scheduled

| Feature | Continuous Mode | Scheduled Mode |
|---------|----------------|----------------|
| **Use Case** | Dedicated server/VPS | GitHub Actions |
| **Runtime** | Forever (24/7) | 11 minutes |
| **Restart** | Auto (Docker) | Manual/Cron |
| **Best For** | Always-on trading | Free tier cloud |
| **Signal Check** | Every 30s | Every 30s |
| **Trading Logic** | Identical | Identical |

---

## 🎯 Best Practices

### For Continuous Mode (Docker)

1. **Monitor regularly**
   ```bash
   # Check every few hours
   ./scripts/status.sh
   ```

2. **Set up alerts** (optional)
   ```bash
   # Monitor with health checks
   ./scripts/monitor.sh
   ```

3. **Review logs daily**
   ```bash
   docker compose logs --tail=100 trading-bot
   ```

4. **Backup trades data**
   ```bash
   ./scripts/backup.sh
   ```

### Resource Usage

Continuous mode is very lightweight:
- **CPU:** ~0.1-0.3% average (spikes to 5-10% during checks)
- **Memory:** ~150-200MB
- **Network:** Minimal (only during trades)

---

## 🐛 Troubleshooting

### Bot Not Trading

1. **Check if in trading hours**
   ```bash
   docker compose logs trading-bot | grep "No signal"
   ```

2. **Verify session filters**
   - Bot may be running but outside session times
   - Check `versions/v1.4/config.json`

3. **Check balance**
   ```bash
   docker compose logs trading-bot | grep "balance"
   ```

### Bot Keeps Restarting

```bash
# Check error logs
docker compose logs trading-bot | grep -i error

# Check health status
docker inspect bot-trade-trading | grep Health -A 10
```

### High Memory Usage

```bash
# Restart to clear memory
docker compose restart trading-bot
```

---

## 🔧 Advanced Configuration

### Change Check Interval

Edit `bot_v1.4.py`:
```python
check_interval = 30  # Change to 60 for every minute
```

### Run Multiple Instances

Edit `docker-compose.yml`:
```yaml
services:
  trading-bot-1:
    # ... config for account 1

  trading-bot-2:
    # ... config for account 2
```

### Custom Command

```yaml
command: ["python", "bot_v1.4.py", "--continuous"]
```

---

## 📝 Summary

**Default Behavior (Docker):**
- ✅ Runs continuously 24/7
- ✅ Auto-restarts if crashed
- ✅ Trades only during configured sessions
- ✅ Perfect for dedicated servers

**To switch to scheduled mode:**
```yaml
# In docker-compose.yml
command: ["python", "bot_v1.4.py"]  # Remove --continuous
```

**Need help?**
- Check logs: `./scripts/logs.sh`
- Check status: `./scripts/status.sh`
- See main docs: [README.md](README.md)
