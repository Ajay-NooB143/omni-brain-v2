#!/bin/bash
# OmniBrain v2 — Deploy Script
# Usage: bash deploy.sh [master|worker-1|worker-2|worker-3]

set -e

ROLE=${1:-master}
REDIS_PASSWORD="L9zarK6YoCN18zcNKk6UKe3VanxcE3QBTVcQ13Xoyrk="
REPO="https://github.com/Ajay-NooB143/omni-brain-v2.git"
DEPLOY_DIR="/home/omni_brain_v2"

echo "=== OmniBrain v2 Deploy — Role: $ROLE ==="

# Install deps
apt-get update -qq && apt-get install -y -qq python3 python3-pip redis-server git

# Clone or pull
if [ -d "$DEPLOY_DIR" ]; then
    cd "$DEPLOY_DIR" && git pull origin main
else
    git clone "$REPO" "$DEPLOY_DIR" && cd "$DEPLOY_DIR"
fi

pip install -r requirements.txt -q

# Redis password (master only)
if [ "$ROLE" = "master" ]; then
    redis-cli CONFIG SET requirepass "$REDIS_PASSWORD"
    redis-cli CONFIG REWRITE
    echo "Redis password set."
fi

# Verify Redis connection
redis-cli -a "$REDIS_PASSWORD" PING

# Create .env if missing
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
REDIS_HOST=__MASTER_IP__
REDIS_PORT=6379
REDIS_PASSWORD=__REDIS_PASSWORD__
ACCOUNT_BALANCE=10000
MAX_DAILY_LOSS=5.0
MASTER_ID=master-prod
WORKER_ID=__WORKER_ID__
PAIRS=__PAIRS__
WORKER_ACCOUNT_BALANCE=3333.33
WORKER_MAX_DAILY_LOSS=2.0
ANTHROPIC_API_KEY=__ANTHROPIC_KEY__
TELEGRAM_BOT_TOKEN=__TELEGRAM_TOKEN__
INSTAGRAM_ACCESS_TOKEN=__INSTAGRAM_TOKEN__
ENVEOF
    echo ".env created — edit with real values: nano $DEPLOY_DIR/.env"
fi

echo "=== Deploy complete for $ROLE ==="
echo "Next: nano $DEPLOY_DIR/.env  (fill in IPs + API keys)"
echo "Then: bash $DEPLOY_DIR/start.sh $ROLE"
