# OMNI BRAIN V2

**Institutional-grade algorithmic trading system** running entirely on Android (UserLand Ubuntu) + VPS.

Multi-timeframe SMC trading engine with AI-powered confidence scoring, correlation arbitrage, dynamic risk management, and Telegram signal distribution.

## Features

### Core Trading Logic

- **Confidence Scoring**: 175-point system (OB + FVG + Sweep + VWAP + Session + Correlation + Yield + Sentiment + Pattern + Divergence) capped at 100
- **Multi-Timeframe Confirmation**: D1 bias → H1 setup → M15 entry precision
- **SMC Market Structure**: Order blocks, fair value gaps, liquidity sweeps, BOS/CHoCH
- **Risk Management**: Dynamic position sizing, adaptive grid, circuit breaker

### Signal Generation

- **Sentiment Analysis**: News + social media + macro events
- **Correlation Arbitrage**: EURUSD vs GBPUSD, XAUUSD vs DXY, sector monitoring
- **Pattern Recognition**: Hidden divergences, institutional clustering, order flow imbalance

### Execution & Monitoring

- **Paper Trader**: Virtual $10k account with P&L tracking
- **Telegram Bot**: Real-time alerts, VIP tier scheduling (free 30min delay, VIP instant)
- **Live MT5 Sync**: Pull current XAUUSD/EURUSD/GBPUSD/SP500/BTC data
- **Logging**: Trade journal, equity curve, drawdown monitoring

### Assets Supported

- **Forex**: EURUSD, GBPUSD, AUDUSD, NZDUSD, USDJPY
- **Commodities**: XAUUSD (Gold), USOIL (Crude Oil)
- **Indices**: SP500 (S&P 500)
- **Crypto**: BTC, ETH, BNB, SOL, XRP

## Architecture

```
omni-brain-v2/
├── core/
│   ├── confidence_scorer.py       # 175-point system
│   ├── mtf_confirmation.py        # D1→H1→M15 validation
│   ├── risk_manager.py            # Position sizing, grid, circuit breaker
│   └── __init__.py
├── modules/
│   ├── sentiment_engine.py        # News/social/macro analysis
│   ├── correlation_engine.py      # Pair correlations, breakdowns
│   ├── telegram_signals.py        # Bot distribution [stub]
│   ├── paper_trader.py            # Virtual trading [stub]
│   └── __init__.py
├── lte_v35_v2.py                  # Orchestrator: integrates all modules
├── tests/
│   └── test_omni_v2.py            # 40+ unit + integration tests
├── pyproject.toml                 # Dependencies, config
└── README.md
```

## Confidence Scoring System

**175-point scale → capped at 100:**

| Component | Points | Triggers |
|-----------|--------|----------|
| Order Block (OB) | 20 | Price inside, multiple touches |
| Fair Value Gap (FVG) | 20 | Proximity, unfilled |
| Liquidity Sweep | 30 | Buy/sell sweep magnitude |
| VWAP | 15 | Price band alignment |
| Session | 15 | London/NY killzone |
| Correlation | 15 | Pair strength |
| Treasury Yield | 10 | USD rate impact |
| Sentiment | 10 | News/social/macro |
| Pattern | 20 | Chart patterns |
| Divergence | 20 | RSI/price hidden divs |
| **TOTAL** | **175** | → **Capped 100** |

**Thresholds:**
- **EXECUTE**: Confidence ≥ 75
- **WAIT**: Confidence 50-74
- **BLOCK**: Confidence < 50

## Setup

### Requirements

- Python 3.11+
- MetaTrader 5 (for live data)
- Telegram Bot Token
- UserLand Ubuntu (on Android) or Linux VPS

### Installation

```bash
# Clone repo
git clone https://github.com/YOUR_USERNAME/omni-brain-v2.git
cd omni-brain-v2

# Install dependencies
pip install -e .

# Install dev tools (testing, linting)
pip install -e ".[dev]"

# Install ML/data extras (optional)
pip install -e ".[ml,data]"
```

### Configuration

Create `.env`:

```bash
MT5_LOGIN=123456789
MT5_PASSWORD=your_password
MT5_SERVER=YourBroker-Demo
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHANNEL_ID=your_channel_id
ACCOUNT_BALANCE=10000
RISK_PERCENT=1.0
MAX_DAILY_LOSS=5.0
```

### Running

```bash
# Start orchestrator
python lte_v35_v2.py

# Run tests
pytest tests/test_omni_v2.py -v

# Check test coverage
pytest tests/test_omni_v2.py --cov=core --cov=modules

# Run specific test
pytest tests/test_omni_v2.py::test_confidence_threshold_execute -v
```

## Usage Example

```python
from lte_v35_v2 import OmniBrainV2
from core.mtf_confirmation import mtf_confirmation_full
from core.confidence_scorer import calculate_confidence, get_signal

# Initialize bot
bot = OmniBrainV2(account_balance=10000, risk_percent=1.0, max_daily_loss=5.0)

# Feed market data
market_data = {
    'EURUSD': {
        'd1': {...},  # Daily OHLC + indicators
        'h1': {...},  # Hourly OHLC + indicators
        'm15': {...}  # 15-min OHLC + indicators
    }
}

# Scan and execute
result = bot.scan_and_execute(market_data)
print(f"Trades opened: {result['trades_opened']}")
print(f"Trades blocked: {result['trades_blocked']}")

# Update open trades
update = bot.update_open_trades(market_data)
print(f"Trades closed: {update['trades_closed']}")

# Get statistics
stats = bot.get_statistics()
print(f"Win rate: {stats['win_rate']}")
print(f"Daily P&L: {stats['daily_pl']}")
```

## Module Documentation

### Core Modules

#### `confidence_scorer.py`

Calculates composite confidence from 10 signal components.

```python
from core.confidence_scorer import calculate_confidence, get_signal

result = calculate_confidence(
    ob=18, fvg=15, sweep=25, vwap=12, session=10,
    corr=12, yield_=8, sentiment=7, pattern=18, divergence=16)

print(result['confidence'])  # 0-100
print(get_signal(result['confidence']))  # EXECUTE, WAIT, or BLOCK
```

#### `mtf_confirmation.py`

Multi-timeframe confirmation: D1 HTF bias → H1 setup → M15 entry.

```python
from core.mtf_confirmation import mtf_confirmation_full

result = mtf_confirmation_full(d1_data, h1_data, m15_data, 'EURUSD')
if result['mtf_status'] == 'CONFIRMED':
    print(f"Enter at ${result['m15_entry']['price']:.4f}")
```

#### `risk_manager.py`

Position sizing, dynamic grid, stop-loss/take-profit, circuit breaker.

```python
from core.risk_manager import calculate_position_size, calculate_dynamic_grid

pos = calculate_position_size(10000, 1.0, 1.0950, 1.0900, 'EURUSD')
print(f"Position: {pos['lots']} lots, Risk: ${pos['risk_amount']}")

grid = calculate_dynamic_grid(confidence=82, market_weather='SUNNY', ...)
print(f"Grid levels: {grid['grid_levels']}, Spacing: {grid['grid_spacing']}")
```

### Modules

#### `sentiment_engine.py`

AI sentiment from news, social, macro events.

```python
from modules.sentiment_engine import forex_sentiment_analyzer

sentiment = forex_sentiment_analyzer(
    pair='EURUSD',
    news_articles=[...],
    social_signals={...},
    macro_events=[...])

print(f"Sentiment: {sentiment['sentiment_label']}")  # BULLISH, NEUTRAL, BEARISH
```

#### `correlation_engine.py`

Pair correlations, breakdown detection, arbitrage signals.

```python
from modules.correlation_engine import detect_correlation_breakdown

breakdown = detect_correlation_breakdown(
    eurusd_data, gbpusd_data, expected_corr=0.85, threshold=0.25)

if breakdown['breakdown']:
    print(f"Trade: {breakdown['trade_signal']}")
```

## Testing

Run full test suite:

```bash
pytest tests/ -v
```

Run specific test category:

```bash
pytest tests/test_omni_v2.py -k "confidence" -v
pytest tests/test_omni_v2.py -k "mtf" -v
pytest tests/test_omni_v2.py -k "risk" -v
```

Run integration tests only:

```bash
pytest tests/ -m integration
```

Check coverage:

```bash
pytest tests/ --cov=core --cov=modules --cov-report=html
```

## Performance Targets

- **Win Rate**: 60%+ (target after 50 trades)
- **Risk/Reward**: 1:2+ (1 unit risk for 2 unit profit)
- **Drawdown**: < 20% (circuit breaker at 5% daily, 10% weekly)
- **Confidence Score**: Execute only ≥75 (< 50 trades/week)

## Roadmap

### v2.1 (Next 2 weeks)

- [ ] Ollama local AI integration for entry validation
- [ ] YouTube → Telegram auto-sync
- [ ] Instagram @forextrader_9 content pipeline
- [ ] 25 advanced innovations (iceberg orders, SMC clusters, chaos theory, etc.)

### v2.2

- [ ] Deep reinforcement learning for threshold optimization
- [ ] Real-time portfolio heatmap visualization
- [ ] Multi-broker MT5 sync (3+ brokers)

### v3.0

- [ ] Cloud deployment (AWS/GCP)
- [ ] Mobile app (iOS/Android)
- [ ] Live subscriber management + payment processing

## Contributing

1. Fork repo
2. Create feature branch: `git checkout -b feature/name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push: `git push origin feature/name`
5. Submit PR

## License

Apache 2.0 — Commercial use permitted.

## Support

- **Issues**: GitHub Issues
- **Docs**: https://docs.omnibrain.io
- **Telegram**: @omnibrainv2_support

## Disclaimer

Trading is risky. Past performance ≠ future results. This system is for educational purposes. Always use proper risk management and test on demo accounts first.

---

**Built for institutional traders.** Run on Android (UserLand) or VPS. No cloud dependencies.
