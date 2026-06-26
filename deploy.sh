#!/bin/bash
# OmniBrain v2 — Redis Bridge Deploy Script
# Usage: bash deploy.sh [master|worker-1|worker-2|worker-3]
# Credentials are stored in Redis, not in Python files.
# No hardcoded secrets in this script.

set -e

ROLE=${1:-master}
REPO="https://github.com/Ajay-NooB143/omni-brain-v2.git"
DEPLOY_DIR="/home/omni_brain_v2"

echo "=== OmniBrain v2 — Redis Bridge Deploy (Role: $ROLE) ==="

# Install deps
apt-get update -qq && apt-get install -y -qq python3 python3-pip redis-server git curl

# Clone or pull
if [ -d "$DEPLOY_DIR" ]; then
    cd "$DEPLOY_DIR" && git pull origin main
else
    git clone "$REPO" "$DEPLOY_DIR" && cd "$DEPLOY_DIR"
fi

pip install -r requirements.txt -q

# Create minimal .env — only Redis connection + bridge URL
if [ ! -f .env ]; then
    cat > .env << 'ENVEOF'
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
BRIDGE_URL=http://localhost:8765
BRIDGE_API_KEY=
ENVEOF
    echo ".env created — edit with: nano $DEPLOY_DIR/.env"
    echo "Set REDIS_PASSWORD and BRIDGE_API_KEY before starting."
fi

echo ""
echo "=== Deploy complete for $ROLE ==="
echo ""
echo "NEXT STEPS:"
echo "  1. Set credentials in .env:  nano $DEPLOY_DIR/.env"
echo "  2. Seed Redis (master only): python3 seed_credentials.py"
echo "  3. Start bridge:             bash $DEPLOY_DIR/start.sh bridge"
echo "  4. Start role:               bash $DEPLOY_DIR/start.sh $ROLE"
