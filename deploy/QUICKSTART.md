# Quick Start Guide - Deploy in 5 Minutes

## Ubuntu Server Deployment

### Step 1: Clone Repository

```bash
git clone https://github.com/TezukaStar/bot-trade.git
cd bot-trade/deploy
```

### Step 2: Run Deployment Script

```bash
./scripts/deploy.sh
```

The script will automatically:
- ✓ Install Docker & Docker Compose
- ✓ Setup environment file
- ✓ Build containers
- ✓ Start services

### Step 3: Configure Credentials

```bash
nano .env
```

Update:
```env
IQ_EMAIL=your_email@example.com
IQ_PASSWORD=your_password
IQ_MODE=PRACTICE
```

Save (Ctrl+X, Y, Enter)

### Step 4: Restart

```bash
./scripts/start.sh
```

**Bot now runs continuously (24/7):**
- ✅ Checks signals every 30 seconds
- ✅ Auto-restarts if crashed
- ✅ Trades only during configured sessions

### Step 5: Access Dashboard

Open browser: `http://your-server-ip:8501`

---

## Daily Operations

### View Logs
```bash
./scripts/logs.sh
```

### Check Status
```bash
./scripts/status.sh
```

### Stop Services
```bash
./scripts/stop.sh
```

### Update Bot
```bash
./scripts/update.sh
```

---

## Bot Operation Modes

### Continuous Mode (Default - Recommended for Dedicated Servers)

**Already enabled by default!** The bot runs 24/7 in Docker:
- ✅ Always monitoring (every 30 seconds)
- ✅ Auto-restarts if crashed
- ✅ No cron needed

View status:
```bash
./scripts/status.sh
```

### Scheduled Mode (Optional - For GitHub Actions)

Use cron if you want scheduled runs instead:
```bash
./scripts/setup-cron.sh
```

**See [CONTINUOUS_MODE.md](CONTINUOUS_MODE.md) for detailed information.**

---

## Using Makefile (Alternative)

```bash
# Build
make build

# Start
make start

# Stop
make stop

# View logs
make logs

# Check status
make status

# Full deployment
make deploy
```

---

## Troubleshooting

### Permission Denied
```bash
chmod +x scripts/*.sh
```

### Container Won't Start
```bash
docker compose logs
docker compose restart
```

### Can't Access Dashboard
```bash
# Check if port 8501 is open
sudo ufw allow 8501/tcp

# Or access via SSH tunnel
ssh -L 8501:localhost:8501 user@server-ip
```

---

## Important Notes

1. **Always test with PRACTICE mode first**
2. **Monitor initial trades closely**
3. **Keep credentials secure**
4. **Review logs regularly**

---

## Need Help?

- Full documentation: [README.md](README.md)
- Check logs: `./scripts/logs.sh`
- GitHub Issues: https://github.com/TezukaStar/bot-trade/issues
