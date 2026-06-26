#!/bin/bash
# OmniBrain v2 — Start Script (Redis Bridge)
# Usage: bash start.sh [master|worker-1|worker-2|worker-3|bridge|stop|status]

set -e

ROLE=${1:-master}
DEPLOY_DIR="/home/omni_brain_v2"
LOG_DIR="$DEPLOY_DIR/logs"

mkdir -p "$LOG_DIR"

# Kill existing
pkill -f "python.*master_bot_runner" 2>/dev/null || true
pkill -f "python.*worker_bot_runner" 2>/dev/null || true
pkill -f "python.*bridge_server" 2>/dev/null || true
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
    bridge)
        echo "Starting Bridge Server (port ${BRIDGE_PORT:-8765})..."
        nohup python3 bridge_server.py > "$LOG_DIR/bridge.log" 2>&1 &
        echo $! > "$LOG_DIR/bridge.pid"
        echo "Bridge PID: $(cat $LOG_DIR/bridge.pid)"
        echo "Logs: tail -f $LOG_DIR/bridge.log"
        ;;
    worker-1|worker-2|worker-3)
        echo "Starting $ROLE..."
        nohup python3 worker_bot_runner.py > "$LOG_DIR/${ROLE}.log" 2>&1 &
        echo $! > "$LOG_DIR/${ROLE}.pid"
        echo "$ROLE PID: $(cat $LOG_DIR/${ROLE}.pid)"
        echo "Logs: tail -f $LOG_DIR/${ROLE}.log"
        ;;
    stop)
        echo "Stopping all processes..."
        pkill -f "python.*master_bot_runner" 2>/dev/null && echo "Master stopped" || echo "Master not running"
        pkill -f "python.*worker_bot_runner" 2>/dev/null && echo "Workers stopped" || echo "Workers not running"
        pkill -f "python.*bridge_server" 2>/dev/null && echo "Bridge stopped" || echo "Bridge not running"
        rm -f "$LOG_DIR"/*.pid
        ;;
    status)
        echo "=== Process Status ==="
        ps aux | grep -E "master_bot_runner|worker_bot_runner|bridge_server" | grep -v grep || echo "No processes running"
        echo ""
        echo "=== Redis Cluster ==="
        source "$DEPLOY_DIR/.env" 2>/dev/null
        redis-cli -a "${REDIS_PASSWORD}" SMEMBERS workers:active 2>/dev/null || echo "Redis not reachable"
        ;;
    *)
        echo "Usage: bash start.sh [master|worker-1|worker-2|worker-3|bridge|stop|status]"
        exit 1
        ;;
esac
