#!/bin/bash
# OmniBrain v2 — Start Script
# Usage: bash start.sh [master|worker-1|worker-2|worker-3]

set -e

ROLE=${1:-master}
DEPLOY_DIR="/home/omni_brain_v2"
LOG_DIR="$DEPLOY_DIR/logs"

mkdir -p "$LOG_DIR"

# Kill existing
pkill -f "python.*master_bot_runner" 2>/dev/null || true
pkill -f "python.*worker_bot_runner" 2>/dev/null || true
sleep 2

cd "$DEPLOY_DIR"

case "$ROLE" in
    master)
        echo "Starting Master Orchestrator..."
        nohup python3 master_bot_runner.py > "$LOG_DIR/master.log" 2>&1 &
        echo $! > "$LOG_DIR/master.pid"
        echo "Master PID: $(cat $LOG_DIR/master.pid)"
        echo "Logs: tail -f $LOG_DIR/master.log"
        ;;
    worker-1)
        echo "Starting Worker-1 (Forex)..."
        WORKER_ID=worker-1 \
        PAIRS=EURUSD,GBPUSD,AUDUSD \
        WORKER_ACCOUNT_BALANCE=3333.33 \
        WORKER_MAX_DAILY_LOSS=2.0 \
        nohup python3 worker_bot_runner.py > "$LOG_DIR/worker-1.log" 2>&1 &
        echo $! > "$LOG_DIR/worker-1.pid"
        echo "Worker-1 PID: $(cat $LOG_DIR/worker-1.pid)"
        echo "Logs: tail -f $LOG_DIR/worker-1.log"
        ;;
    worker-2)
        echo "Starting Worker-2 (Gold/Oil)..."
        WORKER_ID=worker-2 \
        PAIRS=XAUUSD,USOIL \
        WORKER_ACCOUNT_BALANCE=3333.33 \
        WORKER_MAX_DAILY_LOSS=2.0 \
        nohup python3 worker_bot_runner.py > "$LOG_DIR/worker-2.log" 2>&1 &
        echo $! > "$LOG_DIR/worker-2.pid"
        echo "Worker-2 PID: $(cat $LOG_DIR/worker-2.pid)"
        echo "Logs: tail -f $LOG_DIR/worker-2.log"
        ;;
    worker-3)
        echo "Starting Worker-3 (Crypto)..."
        WORKER_ID=worker-3 \
        PAIRS=BTC,ETH,BNB,SOL \
        WORKER_ACCOUNT_BALANCE=3333.34 \
        WORKER_MAX_DAILY_LOSS=2.0 \
        nohup python3 worker_bot_runner.py > "$LOG_DIR/worker-3.log" 2>&1 &
        echo $! > "$LOG_DIR/worker-3.pid"
        echo "Worker-3 PID: $(cat $LOG_DIR/worker-3.pid)"
        echo "Logs: tail -f $LOG_DIR/worker-3.log"
        ;;
    stop)
        echo "Stopping all processes..."
        pkill -f "python.*master_bot_runner" 2>/dev/null && echo "Master stopped" || echo "Master not running"
        pkill -f "python.*worker_bot_runner" 2>/dev/null && echo "Workers stopped" || echo "Workers not running"
        rm -f "$LOG_DIR"/*.pid
        ;;
    status)
        echo "=== Process Status ==="
        ps aux | grep -E "master_bot_runner|worker_bot_runner" | grep -v grep || echo "No processes running"
        echo ""
        echo "=== Redis Cluster ==="
        source "$DEPLOY_DIR/.env" 2>/dev/null
        redis-cli -a "${REDIS_PASSWORD}" SMEMBERS workers:active 2>/dev/null || echo "Redis not reachable"
        ;;
    *)
        echo "Usage: bash start.sh [master|worker-1|worker-2|worker-3|stop|status]"
        exit 1
        ;;
esac
