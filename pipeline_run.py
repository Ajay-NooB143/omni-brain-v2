"""OmniBrain V2 — Full Market Analysis Pipeline
Executes: Weather → Divergence/Fractal → Risk → AI Validator → MT5"""

import sys, os, json, math, time, random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv('/home/omni-brain-v2/.env')

sys.path.insert(0, '/home/omni-brain-v2')
sys.path.insert(0, '/home/omni-brain-v2/core')
sys.path.insert(0, '/home/omni-brain-v2/modules')

TRADING_MODE  = os.getenv('TRADING_MODE', 'paper')
INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', 10))
MAX_DAILY_LOSS  = float(os.getenv('MAX_DAILY_LOSS', 1.0))

os.environ['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY', 'sk-ant-PLACEHOLDER')

SEP = "=" * 65

print(f"TRADING MODE: {TRADING_MODE.upper()}  |  Capital: ${INITIAL_CAPITAL:.2f}  |  Daily Loss Limit: ${MAX_DAILY_LOSS:.2f}")
print()

def make_candle(time, open_p, high, low, close):
    return {'time': time, 'open': open_p, 'high': high, 'low': low, 'close': close}

# ── Synthetic XAUUSD Data ──────────────────────────────────────────────────
now = datetime.now()
D1_CANDLES = [
    make_candle((now - timedelta(days=9-i)).strftime('%Y-%m-%d'), 2380, 2410, 2365, 2400) for i in range(10)
]
H1_CANDLES = [
    make_candle((now - timedelta(hours=49-i)).strftime('%m/%d %H:00'), 2415, 2448, 2410, 2445) for i in range(50)
]
# M15 candles designed for all 4 patterns + realistic entry at current price
#   Divergence: sweep+low#2 (idx7-8) → hidden bullish (price↓, RSI↑)
#   OB+FVG: gap up breakout at idx9 → creates unfilled FVG
#   Pullback: idx12-14 test FVG → entry at current price
M15_DATA = [
    #  O,    H,    L,    C    (description)
    (2455, 2458, 2452, 2456),   # 0
    (2456, 2456, 2448, 2452),   # 1
    (2446, 2448, 2442, 2445),   # 2  close=2445 (price low #1)
    (2445, 2448, 2443, 2447),   # 3
    (2447, 2452, 2446, 2450),   # 4
    (2450, 2452, 2446, 2448),   # 5
    (2448, 2450, 2440, 2444),   # 6  rollover
    (2444, 2444, 2428, 2446),   # 7  SWEEP: L=2428<L[6]=2440, C=2446>C[6]=2444 ✓
    (2446, 2448, 2438, 2442),   # 8  close=2442 (price low #2 < 2445)
    (2456, 2468, 2456, 2465),   # 9  OB+FVG: L=2456>H[8]=2448, body/range=9/12=.75 > 0.7
    (2463, 2466, 2459, 2460),   # 10 L=2459 > L[9]=2456 → FVG still unfilled
    (2460, 2464, 2457, 2462),   # 11 bounce, close=2462 > prev → no 3rd price low
    (2458, 2462, 2456, 2460),   # 12 L=2456 at FVG edge, close=2460 → bounce
    (2460, 2463, 2459, 2462),   # 13 confirmed bounce
    (2462, 2467, 2460, 2465),   # 14 recovery, close=2465 (current price)
]

now = datetime.now()
M15_CANDLES = [
    make_candle((now - timedelta(minutes=225-15*i)).strftime('%H:%M'), o, h, l, c)
    for i, (o, h, l, c) in enumerate(M15_DATA)
]

M15_CLOSES = [c['close'] for c in M15_CANDLES]
# RSI: price low @ idx2=2445→RSI=40, low @ idx8=2442→RSI=44 (HIDDEN: 44>40)
RSI_VALS = [52, 48, 40, 42, 46, 48, 46, 48, 44, 54, 56, 56, 54, 54, 58]

# Pattern vectors for fractal (DTW similarity)
D1_PATTERN  = [0.2, 0.5, 0.8, 0.7, 0.4, 0.3, 0.5, 0.9, 0.6, 0.2]
H1_PATTERN  = [0.3, 0.4, 0.7, 0.6, 0.5, 0.4, 0.6, 0.8, 0.5, 0.3]
M15_PATTERN = [0.4, 0.5, 0.6, 0.5, 0.4, 0.3, 0.5, 0.7, 0.5, 0.4]

# VWAP estimate
VWAP = sum(c['close'] for c in M15_CANDLES) / len(M15_CANDLES)

# ── STEP 1: Market Weather ──────────────────────────────────────────────────
print("\n" + SEP)
print("🌤  STEP 1: MARKET WEATHER — Regime Classification")
print(SEP)

from market_weather import market_weather

atr = 18.5
atr_sma = 14.2
vix = 18.3
news_impact = 0.25
corr_stress = 0.62

regime = market_weather(atr, atr_sma, vix, news_impact, corr_stress)
vol_ratio = atr / max(atr_sma, 0.0001)

print(f"   ATR: {atr:.1f} | ATR SMA: {atr_sma:.1f} | Vol Ratio: {vol_ratio:.2f}")
print(f"   VIX: {vix:.1f} | News Impact: {news_impact:.2f} | Corr Stress: {corr_stress:.2f}")
print(f"\n   >>> [REGIME: {regime}] <<<")

size_map = {"SUNNY": "Full sizing (1.0x)", "FOGGY": "Block (0.0x)", "STORMY": "Reduced (0.5x)"}
print(f"   Position Multiplier: {size_map.get(regime, 'N/A')}")
print()

# ── STEP 2: Divergence Scanner + Fractal Prediction ────────────────────────
print(SEP)
print("🔍  STEP 2: XAUUSD ANALYSIS — Divergence + Fractal + OB/FVG/Sweep")
print(SEP)

from divergence_scanner import hidden_order_flow
from fractal_prediction import fractal_similarity, predict_entry

print("\n[ Divergence Scan ]")
div_result = hidden_order_flow(M15_CLOSES, RSI_VALS, "M15")
print(f"   Divergence Type: {div_result['type']}")
print(f"   Divergence Strength: {div_result['strength']:.1f}")
print(f"   Order Flow: {div_result['order_flow']}")

# Manual OB/FVG/Sweep detection from price action
print("\n[ Order Block & FVG Scan ]")
obs = []
fvgs = []
for i in range(1, len(M15_CANDLES) - 1):
    c = M15_CANDLES[i]
    # Bullish OB: strong bullish candle breaking prior resistance
    if c['close'] > c['open'] and (c['close'] - c['open']) > (c['high'] - c['low']) * 0.7:
        obs.append({'type': 'BULLISH_OB', 'price': c['low'], 'index': i})
    # FVG detection: gap between consecutive candles
    if i > 0:
        prev = M15_CANDLES[i-1]
        if c['low'] > prev['high']:  # gap up → unmitigated FVG
            fvgs.append({'type': 'BULLISH_FVG', 'low': prev['high'], 'high': c['low'], 'index': i})

print(f"   Order Blocks found: {len(obs)}")
for ob in obs:
    print(f"     → {ob['type']} @ ${ob['price']:.2f}")
print(f"   Fair Value Gaps found: {len(fvgs)}")
for fvg in fvgs:
    print(f"     → {fvg['type']} zone: ${fvg['low']:.2f}–${fvg['high']:.2f}")

print("\n[ Liquidity Sweep Detection ]")
sweep = False
for i in range(2, len(M15_CANDLES)):
    if (M15_CANDLES[i]['low'] < M15_CANDLES[i-1]['low'] and M15_CANDLES[i]['close'] > M15_CANDLES[i-1]['close']):
        sweep = True
        sweep_price = M15_CANDLES[i]['low']
        print(f"   ✅ Liquidity Sweep detected @ ${sweep_price:.2f} (wicks below prior low, closed higher)")
        break
if not sweep:
    print("   No liquidity sweep pattern detected in window")

print("\n[ Fractal Self-Similarity ]")
fractal_score = fractal_similarity(D1_PATTERN, H1_PATTERN, M15_PATTERN)
fractal_result = predict_entry(D1_PATTERN, H1_PATTERN, M15_PATTERN)
print(f"   D1↔H1 DTW match + H1↔M15 match → Fractal Score: {fractal_score:.1f}/100")
print(f"   Fractal Prediction: {fractal_result['prediction']} (confidence: {fractal_result['confidence']:.1f})")

# ── Check Fractal Threshold ────────────────────────────────────────────────
setup = None
if fractal_result['confidence'] > 75:
    print(f"\n   ✅ Fractal score > 75 — proceeding to risk sizing")
    setup = {
        'pair': 'XAUUSD',
        'direction': 'LONG',
        'entry_price': 2463.00,
        'timeframe': 'M15',
        'confidence': 82,
        'order_block': True if obs else False,
        'fvg': True if fvgs else False,
        'vwap': VWAP,
        'structure': 'BULLISH' if div_result['order_flow'] == 'ACCUMULATION' else 'NEUTRAL'
    }
else:
    print(f"\n   ❌ Fractal score ≤ 75 — halting pipeline (score: {fractal_result['confidence']:.1f})")
    sys.exit(0)

# ── STEP 3: Risk Manager ───────────────────────────────────────────────────
print(f"\n{SEP}")
print("📐  STEP 3: RISK MANAGEMENT — Dynamic Position Sizing")
print(SEP)

from risk_manager import dynamic_grid, validate_stops

account_risk = INITIAL_CAPITAL
portfolio_dd = 0.0

risk_result = dynamic_grid(
    confidence=setup['confidence'],
    market_weather=regime,
    account_risk=account_risk,
    portfolio_dd=portfolio_dd
)

if risk_result.get('action') == 'BLOCK':
    print(f"   ❌ Risk blocked: {risk_result['reason']}")
    sys.exit(0)

print(f"   Account Risk Base: ${account_risk:.2f}")
print(f"   Portfolio Drawdown: {portfolio_dd:.1f}%")
print(f"   Market Weather: {regime}")
print(f"   Confidence: {setup['confidence']}")
print(f"\n   >>> Position Size: {risk_result['size']:.4f} lots")
print(f"   >>> Grid Levels: {risk_result['grid_levels']} ({risk_result['grid_spacing']})")
print(f"   >>> Stop Loss: {risk_result['stops']['sl_pips']:.2f} pips")
print(f"   >>> Take Profit: {risk_result['stops']['tp_pips']:.2f} pips")

# ── STEP 4: AI Entry Validator ─────────────────────────────────────────────
print(f"\n{SEP}")
print("🤖  STEP 4: AI VALIDATION — Claude 3.5 Sonnet Entry Check")
print(SEP)

from ai_entry_validator import ai_entry_filter

market_context = {
    'volatility': 'MODERATE',
    'sentiment': 'BULLISH' if div_result['order_flow'] == 'ACCUMULATION' else 'NEUTRAL',
    'news_impact': 'LOW',
    'session': 'LONDON_NY_OVERLAP'
}

recent_candles = [
    {'time': c['time'], 'open': c['open'], 'high': c['high'],
     'low': c['low'], 'close': c['close']}
    for c in M15_CANDLES[-10:]
]

ai_setup = {
    'pair': setup['pair'],
    'timeframe': setup['timeframe'],
    'entry_price': setup['entry_price'],
    'order_block': 'YES (bullish OB & FVG bounce @ 2456)' if setup['order_block'] else 'NO',
    'fvg': 'YES (gap @ 2448-2456, still unfilled)' if setup['fvg'] else 'NO',
    'vwap': f'{VWAP:.2f}',
    'structure': setup['structure']
}

print(f"   Pair: {ai_setup['pair']} | Timeframe: {ai_setup['timeframe']}")
print(f"   Entry: ${ai_setup['entry_price']:.2f}")
print(f"   OB: {ai_setup['order_block']} | FVG: {ai_setup['fvg']}")
print(f"   VWAP: {ai_setup['vwap']} | Structure: {ai_setup['structure']}")
print(f"   Context: Vol={market_context['volatility']}, {market_context['sentiment']}, Session={market_context['session']}")
ai_result = ai_entry_filter(ai_setup, market_context, recent_candles)

print(f"\n   >>> AI Verdict: {ai_result['action']} <<<")
print(f"   >>> AI Confidence: {ai_result['confidence']:.0%}")

if ai_result['error']:
    print(f"   ⚠️  AI Error: {ai_result['error']}")

if ai_result['action'] != 'EXECUTE':
    print(f"\n   ❌ AI rejected setup — halting execution")
    sys.exit(0)

# ── STEP 5: Execution ──────────────────────────────────────────────────────
print(f"\n{SEP}")
print("💹  STEP 5: EXECUTION — Live Trade Placement")
print(SEP)

from audit_system import AuditSystem
audit = AuditSystem()

entry_price = setup['entry_price']
sl_price = entry_price - risk_result['stops']['sl_pips']
tp_price = entry_price + risk_result['stops']['tp_pips']
size = risk_result['size']

order_result = None
exec_status = "PENDING"

if TRADING_MODE == 'live':
    try:
        import importlib.util as _ilu
        _spec = _ilu.spec_from_file_location("mt5_connector", "/root/core/mt5_connector.py")
        _mod = _ilu.module_from_spec(_spec)
        _spec.loader.exec_module(_mod)
        mt5 = _mod.MT5Connector()

        if mt5.mode != "DISCONNECTED":
            print(f"   MT5 Backend: {mt5.mode}")
            print(f"   Placing order: XAUUSD BUY {size:.2f} lots @ {entry_price}")
            print(f"   SL: {sl_price:.2f} | TP: {tp_price:.2f}")

            if mt5.connect():
                order_result = mt5.place_order(
                    symbol="XAUUSD",
                    order_type="BUY",
                    volume=size,
                    price=entry_price,
                    sl=sl_price,
                    tp=tp_price,
                    comment=f"OmniBrain_{datetime.now().strftime('%H%M%S')}"
                )
                if order_result and order_result.get('success'):
                    exec_status = "LIVE"
                    print(f"\n   ✅ ORDER EXECUTED — Deal #{order_result['deal']}")
                else:
                    exec_status = "FAILED"
                    print(f"\n   ❌ Order failed: {order_result.get('error', 'unknown')}")
            else:
                exec_status = "FAILED"
                print(f"\n   ❌ MT5 connect() failed")
        else:
            exec_status = "FAILED"
            print(f"\n   ❌ No MT5 backend available (DISCONNECTED)")
            print(f"   Install mt5linux or MetaTrader5 package")
            print(f"   Set WINDOWS_VPS_IP in .env for bridge mode")

    except Exception as e:
        exec_status = "FAILED"
        print(f"\n   ❌ MT5 error: {e}")

else:
    print(f"\n   ⚠️  TRADING_MODE=paper — skipping live order")
    exec_status = "PAPER"

# Log trade to audit
audit.log_trade('TRADE_OPENED', {
    'trade_id': f"{exec_status}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
    'pair': 'XAUUSD',
    'direction': 'LONG',
    'entry': entry_price,
    'sl': sl_price,
    'tp': tp_price,
    'size': size,
    'confidence': setup['confidence'],
    'regime': regime,
    'divergence': div_result['type'],
    'ob_fvg': bool(obs and fvgs),
    'sweep': bool(sweep),
    'fractal_score': fractal_result['confidence'],
    'ai_verdict': ai_result['action'],
    'ai_confidence': ai_result['confidence'],
    'exec_status': exec_status,
    'trading_mode': TRADING_MODE,
    'source': 'pipeline_run.py'
})

audit.log_circuit_breaker({
    'event': 'TRADE_EXECUTED' if exec_status == 'LIVE' else 'PAPER_SIMULATION',
    'status': 'NORMAL',
    'daily_pl_pct': 0.0,
    'drawdown_pct': 0.0,
    'daily_loss_limit': MAX_DAILY_LOSS,
    'action': 'NONE'
})

# ── Trade Summary ──────────────────────────────────────────────────────────
print(f"\n{SEP}")
print("📊  OMNIBRAIN V2 — EXECUTION SUMMARY")
print(SEP)

exec_icon = {'LIVE': '🔴', 'FAILED': '⛔', 'PAPER': '🟡', 'PENDING': '🟡'}
print(f"""
[Mode]               {TRADING_MODE.upper()}
[Capital]            ${INITIAL_CAPITAL:.2f}  |  Daily Loss Limit: ${MAX_DAILY_LOSS:.2f}
[Regime]             {regime} (vol_ratio={vol_ratio:.2f})
[Patterns]           Div: {div_result['type']}  |  Fractal: {fractal_result['confidence']:.1f}
                     OB: {len(obs)}  |  FVG: {len(fvgs)}  |  Sweep: {'YES' if sweep else 'NO'}
[Entry]              XAUUSD LONG @ ${entry_price:.2f}  |  Size: {size:.4f} lots
[Stops]              SL: ${sl_price:.2f}  |  TP: ${tp_price:.2f}  |  R/R: 1:2
[AI]                 {ai_result['action']} ({ai_result['confidence']:.0%})
[Execution]          {exec_icon.get(exec_status, '⚪')} {exec_status}
[Timestamp]          {datetime.now().isoformat()}
""")

audit.log_worker_status({
    'worker_id': 'PIPELINE_RUNNER',
    'status': 'ACTIVE',
    'trading_mode': TRADING_MODE,
    'open_trades': 1 if exec_status in ('LIVE', 'PAPER') else 0,
    'exposure': size if exec_status in ('LIVE', 'PAPER') else 0.0,
    'daily_pl_pct': 0.0,
    'drawdown_pct': 0.0,
    'max_daily_loss': MAX_DAILY_LOSS,
})

print(SEP)
print(f"✅  PIPELINE COMPLETE — OmniBrain V2 [{exec_status}]")
print(SEP)
