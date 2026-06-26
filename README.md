# OmniBrain v2 — Multi-Timeframe Forex Trading System

Redis-bridged cluster deployment for algorithmic trading with AI validation, fractal pattern recognition, dynamic risk management, and tiered signal delivery.

**Credentials live in Redis, not in Python files.** No hardcoded secrets. All VPS instances read their config from a central Redis bridge.

## Architecture

```
                    BRIDGE SERVER (HTTP API)
                    [master VPS :8765]
                          |
                    REDIS (credential store + message bus)
                          |
         ________________|________________
         |                |                |
   WORKER-1         WORKER-2       WORKER-3
 (EU pairs)       (GOLD/OIL)      (CRYPTO)
         |                |                |
   [BLPOP queue]   [BLPOP queue]   [BLPOP queue]
      |________________|________________|
                       |
              AUDIT SYSTEM (Redis Lists)
                 + MT5 BRIDGE (Windows VPS)
```

### Key Differences from V1
- **No hardcoded IPs/passwords** — all config in Redis `creds:*` hashes
- **`bridge_server.py`** — HTTP API for VPS registration + MT5 bridge
- **`redis_bridge.py`** — single import for all credential reads
- **`seed_credentials.py`** — one-time Redis population script

## Features

### Core Trading Engine
- **Market Weather Classification** - SUNNY/FOGGY/STORMY regimes via ATR ratio, VIX, correlation stress
- **Fractal Prediction** - Cross-timeframe self-similarity (DTW on D1/H1/M15) for entry prediction
- **Dynamic Risk Management** - Adaptive position sizing + grid levels based on confidence & market weather
- **Hidden Divergence Scanner** - RSI/price divergence → institutional order flow detection
- **Correlation Breakdown Alerts** - Arbitrage alerts (e.g., XAUUSD vs DXY deviation > 0.25)

### AI Validation
- **Claude 3.5 Sonnet Integration** - Real-time setup validation (EXECUTE/REFINE/BLOCK)
- **Two-pass Analysis** - Verdict + risk/reward assessment

### Signal Delivery
- **Tiered Subscriptions** - VIP (instant, 2x size), PRO (15min delay, 1.5x), FREE (30min delay, 1x)
- **Yield Arbitrage Radar** - Treasury yield spike → DXY/Gold/JPY cascade detection
- **Content-Trade Sync** - YouTube/Instagram → Telegram bridge with 15min delay

### Cluster Architecture
- **Master Orchestrator** - Work distribution, circuit breakers, cluster health monitoring
- **3 Specialized Workers** - EU pairs, Gold/Oil, Crypto
- **Central Audit System** - Compliance logging, CSV export, circuit breaker tracking
- **PM2 Process Management** - Auto-restart, logging, startup persistence

## Quick Start

### Prerequisites
- Python 3.11+
- Redis server
- Anthropic API key
- 4 VPS instances (1 master + 3 workers)

### Local Development

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/omni-brain-v2.git
cd omni-brain-v2

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with Redis connection

# Start Redis
redis-server --daemonize yes

# Seed credentials into Redis (one time)
python seed_credentials.py --api-key 'sk-ant-xxx'

# Start bridge server (terminal 1)
python bridge_server.py

# Run master (terminal 2)
python master_bot_runner.py

# Run worker (terminal 3)
WORKER_ID=worker-1 PAIRS=EURUSD,GBPUSD,AUDUSD python worker_bot_runner.py
```

### Production Deployment (Redis Bridge)

No SSH between VPS instances. Everything flows through Redis.

```bash
# 1. Deploy master VPS
ssh root@master_vps
bash deploy.sh master
nano .env                              # set REDIS_PASSWORD + BRIDGE_API_KEY
python seed_credentials.py --api-key 'sk-ant-xxx' --broker-host 'windows_vps_ip'
bash start.sh bridge                   # starts HTTP API on port 8765
bash start.sh master

# 2. Register workers (from any machine)
curl -X POST http://<MASTER_IP>:8765/register \
  -H 'X-API-Key: <key>' \
  -d '{"role":"worker-1","ip":"<WORKER_IP>","pairs":["EURUSD","GBPUSD","AUDUSD"]}'

# 3. Deploy worker VPS
ssh root@worker1_vps
bash deploy.sh worker-1
nano .env                              # set REDIS_HOST=<MASTER_IP> + REDIS_PASSWORD
bash start.sh worker-1
```

## Project Structure

```
omni-brain-v2/
├── core/                          # Trading analysis engines
│   ├── market_weather.py          # Regime classification
│   ├── fractal_prediction.py      # DTW cross-timeframe analysis
│   ├── risk_manager.py            # Adaptive sizing & grids
│   ├── divergence_scanner.py      # Hidden RSI divergence
│   └── correlation_breakdown.py   # Correlation arbitrage
├── modules/                       # Application modules
│   ├── ai_entry_validator.py      # Claude 3.5 validation
│   ├── subscription_signals.py    # Tiered delivery
│   ├── yield_arbitrage_radar.py   # Yield spike detection
│   └── ...                        # Sentiment, geopolitics, etc.
├── redis_bridge.py                # Credential bridge (all secrets from Redis)
├── bridge_server.py               # HTTP API for VPS registration + MT5 bridge
├── seed_credentials.py            # One-time Redis credential seeder
├── master_bot.py                  # Cluster orchestrator
├── worker_bot.py                  # Worker execution engine
├── audit_system.py                # Compliance logging
├── cluster_config.py              # Config reader (reads from Redis bridge)
├── master_bot_runner.py           # Master entry point
├── worker_bot_runner.py           # Worker entry point
├── deploy.sh                      # VPS deployment script
├── start.sh                       # Start/stop/status
└── requirements.txt
```

## Key Thresholds

| Parameter | Value | Description |
|-----------|-------|-------------|
| Fractal Score | > 75 | Valid self-similar pattern |
| Correlation Deviation | > 0.25 | Arbitrage trigger |
| Yield Spike | > 0.05 (5bps) | Cascade alert |
| Market Weather STORMY | ATR ratio > 2.0 or corr > 0.85 | 0.5x size |
| Market Weather FOGGY | News impact > 0.7 | Block trades |
| Worker Daily Loss | > 2% | Pause worker |
| Cluster Daily Loss | > 5% | Stop all |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| REDIS_HOST | Yes | Redis host (master IP for workers) |
| REDIS_PORT | Yes | Redis port (default 6379) |
| REDIS_PASSWORD | Yes | Redis password |
| BRIDGE_URL | No | HTTP bridge URL for bootstrap |
| BRIDGE_API_KEY | No | Bridge API key for auth |

All other configs (API keys, broker config, VPS IPs, worker pairs) are stored in Redis hashes and managed via `seed_credentials.py` or the bridge API.

## Compliance & Auditing

The audit system logs:
- All trade opens/closes with full context
- Worker status heartbeats (every 30s)
- Circuit breaker events (cluster + worker level)
- Daily compliance reports (CSV export)

Generate report:
```bash
python generate_report.py
```

## Gotchas

1. **AI Validator Latency** - 2 sequential Claude calls (~2-4s), run async in production
2. **Tier Multipliers** - VIP 2x, PRO 1.5x position size; ensure risk limits account for this
3. **Async Bridges** - Social media bridges use `schedule_alert` / background workers
4. **Hardcoded Correlations** - XAUUSD/DXY = -0.95; update if regime shifts
5. **Redis Persistence** - Enable AOF/RDB for audit trail durability

## License

Proprietary - OmniBrain v2 Trading System