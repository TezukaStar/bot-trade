# Bot Trade - Docker Deployment Guide

Deploy bot-trade on Ubuntu server using Docker and Docker Compose.

## 📋 Prerequisites

- Ubuntu 20.04 or later
- Minimum 2GB RAM, 10GB disk space
- Root or sudo access
- Internet connection

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/TezukaStar/bot-trade.git
cd bot-trade/deploy
```

### 2. Run Automated Deployment

```bash
./scripts/deploy.sh
```

This script will:
- Install Docker and Docker Compose (if not present)
- Set up environment file
- Build Docker images
- Start all services

### 3. Configure Credentials

Edit the `.env` file with your IQ Option credentials:

```bash
nano .env
```

```env
IQ_EMAIL=your_email@example.com
IQ_PASSWORD=your_password
IQ_MODE=PRACTICE  # or REAL
```

### 4. Restart Services

```bash
./scripts/start.sh
```

### 5. Access Dashboard

Open your browser and navigate to:
- **Local:** http://localhost:8501
- **Remote:** http://your-server-ip:8501

---

## 📁 Project Structure

```
deploy/
├── docker-compose.yml        # Main orchestration file
├── Dockerfile.bot            # Trading bot container
├── Dockerfile.dashboard      # Dashboard container
├── .env.example              # Environment template
├── nginx/
│   └── nginx.conf            # Nginx reverse proxy config
├── scripts/
│   ├── deploy.sh             # Automated deployment
│   ├── start.sh              # Start services
│   ├── stop.sh               # Stop services
│   ├── logs.sh               # View logs
│   ├── status.sh             # Check service status
│   ├── update.sh             # Update and restart
│   └── setup-cron.sh         # Setup automated trading schedule
└── README.md                 # This file
```

---

## 🔧 Manual Installation

### Step 1: Install Docker

```bash
# Update package index
sudo apt-get update

# Install dependencies
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Add Docker's GPG key
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | \
  sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add user to docker group
sudo usermod -aG docker $USER

# Log out and log back in for changes to take effect
```

### Step 2: Setup Environment

```bash
cd bot-trade/deploy

# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env
```

### Step 3: Build and Start

```bash
# Build images
docker compose build

# Start services
docker compose up -d

# Check status
docker compose ps
```

---

## 📜 Available Scripts

### `deploy.sh`
Automated deployment script. Installs Docker, builds images, and starts services.

```bash
./scripts/deploy.sh
```

### `start.sh`
Start all services.

```bash
./scripts/start.sh
```

### `stop.sh`
Stop all services.

```bash
./scripts/stop.sh
```

### `logs.sh`
View logs from services.

```bash
# All services
./scripts/logs.sh

# Specific service
./scripts/logs.sh trading-bot
./scripts/logs.sh dashboard
./scripts/logs.sh nginx
```

### `status.sh`
Check service status and resource usage.

```bash
./scripts/status.sh
```

### `update.sh`
Pull latest code, rebuild, and restart services.

```bash
./scripts/update.sh
```

### `setup-cron.sh`
Setup automated trading schedule using cron.

```bash
./scripts/setup-cron.sh
```

This will run the bot:
- **Every 30 minutes (24/7)** - Bot checks trading_hours and session_filters internally
- Only trades when conditions match config (EURUSD, EURUSD-OTC, EURCAD sessions)

---

## 🐳 Docker Commands

### View Running Containers

```bash
docker compose ps
```

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f trading-bot
docker compose logs -f dashboard
```

### Restart Services

```bash
docker compose restart
```

### Stop and Remove

```bash
docker compose down
```

### Rebuild Images

```bash
docker compose build --no-cache
```

### Execute Commands in Container

```bash
# Access bot container
docker compose exec trading-bot bash

# Access dashboard container
docker compose exec dashboard bash
```

---

## 🔒 Security Recommendations

### 1. Use Strong Passwords
- Change default credentials
- Use complex passwords for IQ Option account

### 2. Enable Firewall

```bash
# Install UFW
sudo apt-get install ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS (if using nginx)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow Streamlit (or restrict to specific IPs)
sudo ufw allow 8501/tcp

# Enable firewall
sudo ufw enable
```

### 3. Setup SSL/TLS

For production, enable HTTPS:

1. Install certbot:
```bash
sudo apt-get install certbot
```

2. Get SSL certificate:
```bash
sudo certbot certonly --standalone -d your-domain.com
```

3. Copy certificates to nginx:
```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem deploy/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem deploy/nginx/ssl/key.pem
```

4. Uncomment HTTPS server block in `nginx/nginx.conf`

5. Restart nginx:
```bash
docker compose restart nginx
```

### 4. Restrict Access

Edit `docker-compose.yml` to bind dashboard to localhost only:

```yaml
ports:
  - "127.0.0.1:8501:8501"
```

Then use SSH tunnel to access:

```bash
ssh -L 8501:localhost:8501 user@your-server-ip
```

---

## 🔄 Automated Trading Setup

### Using Cron (Recommended)

```bash
./scripts/setup-cron.sh
```

This sets up cron jobs to run the bot during premium sessions.

### Manual Cron Setup

```bash
crontab -e
```

Add:

```cron
# Run every 30 minutes (24/7)
# Bot checks trading_hours and session_filters internally
*/30 * * * * cd /path/to/bot-trade/deploy && docker compose run --rm trading-bot >> cron.log 2>&1
```

### Using Systemd Timer (Alternative)

Create `/etc/systemd/system/bot-trade.service`:

```ini
[Unit]
Description=Bot Trade Trading Bot
After=docker.service

[Service]
Type=oneshot
WorkingDirectory=/path/to/bot-trade/deploy
ExecStart=/usr/bin/docker compose run --rm trading-bot

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/bot-trade.timer`:

```ini
[Unit]
Description=Bot Trade Trading Schedule

[Timer]
# Run every 30 minutes (24/7)
OnCalendar=*:0/30
Persistent=true

[Install]
WantedBy=timers.target
```

Enable:

```bash
sudo systemctl enable bot-trade.timer
sudo systemctl start bot-trade.timer
```

---

## 📊 Monitoring

### View Dashboard

Access real-time metrics at: http://your-server-ip:8501

### Check Logs

```bash
# Real-time logs
./scripts/logs.sh

# Recent activity
docker compose logs --tail=100

# Cron logs (if using cron)
tail -f deploy/cron.log
```

### Resource Usage

```bash
docker stats

# Or use the status script
./scripts/status.sh
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
docker compose logs

# Rebuild
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Connection Issues

```bash
# Test IQ Option connection
docker compose run --rm trading-bot python -c "from iqoptionapi.stable_api import IQ_Option; print('OK')"

# Check network
docker network ls
docker network inspect deploy_bot-network
```

### Permission Denied

```bash
# Fix file permissions
sudo chown -R $USER:$USER .

# Fix script permissions
chmod +x scripts/*.sh
```

### Out of Disk Space

```bash
# Clean up old images
docker system prune -a

# Remove unused volumes
docker volume prune
```

### Bot Not Trading

1. Check if credentials are correct in `.env`
2. Verify trading hours (must be within session times)
3. Check if account has sufficient balance
4. Review logs for errors: `docker compose logs trading-bot`

---

## 🔄 Backup and Recovery

### Backup Trade Data

```bash
# Backup trades.csv
docker compose cp trading-bot:/app/data/trades.csv ./backup/trades_$(date +%Y%m%d).csv

# Or access volume directly
docker volume inspect deploy_trades-data
```

### Restore Trade Data

```bash
# Copy backup into container
docker compose cp ./backup/trades.csv trading-bot:/app/data/trades.csv
```

### Full Backup

```bash
# Backup everything
tar -czf bot-trade-backup-$(date +%Y%m%d).tar.gz \
  docker-compose.yml \
  .env \
  nginx/ \
  scripts/

# Backup Docker volumes
docker run --rm -v deploy_trades-data:/data -v $(pwd):/backup \
  ubuntu tar czf /backup/trades-data-backup.tar.gz /data
```

---

## 📈 Performance Tuning

### Adjust Resource Limits

Edit `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### Optimize Logging

Reduce log size:

```yaml
logging:
  driver: "json-file"
  options:
    max-size: "5m"
    max-file: "2"
```

---

## 🆘 Support

- **Issues:** https://github.com/TezukaStar/bot-trade/issues
- **Documentation:** See main README.md
- **Logs:** Check `docker compose logs` for detailed errors

---

## ⚠️ Important Notes

1. **Always test with PRACTICE mode first**
2. **Monitor initial trades closely**
3. **Keep credentials secure**
4. **Regularly backup trade data**
5. **Update software periodically**
6. **Review logs for unusual activity**
7. **Understand that trading involves risk**

---

## 📝 License

This deployment configuration is part of the bot-trade project.
See main repository for license information.
