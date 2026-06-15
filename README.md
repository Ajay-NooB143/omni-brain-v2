# OmniBrain v2 - Multi-Timeframe Forex Trading System

A hierarchical cluster deployment for algorithmic forex trading with AI validation, fractal pattern recognition, dynamic risk management, and tiered signal delivery.

## Architecture

```
                    MASTER BOT (Main Orchestrator)
                    [master.example.com]
                         |
         ________________|________________
         |                |                |
   WORKER-1         WORKER-2       WORKER-3
 [worker1.com]    [worker2.com]   [worker3.com]
 (EU pairs)       (GOLD/OIL)      (CRYPTO)
         |                |                |
   [Redis Queue]   [Redis Queue]   [Redis Queue]
      |________________|________________|
                       |
                  AUDIT SYSTEM
            (Central Logging/Compliance)
            [Redis Backend]
```

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
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your keys

# Start Redis
redis-server --daemonize yes

# Run master (terminal 1)
python master_bot_runner.py

# Run worker (terminal 2)
WORKER_ID=worker-1 PAIRS=EURUSD,GBPUSD,AUDUSD ACCOUNT_BALANCE=3333.33 python worker_bot_runner.py
```

### Production Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for full 4-VPS deployment instructions.

## Project Structure

```
omni-brain-v2/
├── core/
│   ├── market_weather.py      # Regime classification
│   ├── fractal_prediction.py  # DTW cross-timeframe analysis
│   ├── risk_manager.py        # Adaptive sizing & grids
│   ├── divergence_scanner.py  # Hidden RSI divergence
│   └── correlation_breakdown.py # Correlation arbitrage
├── modules/
│   ├── ai_entry_validator.py     # Claude 3.5 validation
│   ├── subscription_signals.py   # Tiered delivery
│   ├── yield_arbitrage_radar.py  # Yield spike detection
│   ├── youtube_telegram_sync.py  # YT → Telegram
│   └── instagram_telegram_bridge.py # IG → Telegram
├── master_bot.py           # Cluster orchestrator
├── worker_bot.py           # Worker execution engine
├── audit_system.py         # Compliance logging
├── cluster_config.py       # VPS configuration
├── master_bot_runner.py    # Master entry point
├── worker_bot_runner.py    # Worker entry point
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
| ANTHROPIC_API_KEY | Yes | Claude API key for AI validation |
| REDIS_HOST | Yes | Master Redis IP |
| REDIS_PORT | Yes | Redis port (default 6379) |
| WORKER_ID | Workers only | worker-1, worker-2, or worker-3 |
| PAIRS | Workers only | Comma-separated pair list |
| ACCOUNT_BALANCE | Yes | Allocated capital |
| MAX_DAILY_LOSS | Yes | Circuit breaker % |

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