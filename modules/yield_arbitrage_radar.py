def treasury_yield_correlation(usd_yield_10y, dxy, xauusd, usd_jpy, usd_yield_10y_prev_candle):
    """Monitor yield spikes → DXY pump → asset cascades"""
    yield_change = usd_yield_10y - usd_yield_10y_prev_candle
    
    if yield_change > 0.05:  # Significant spike (5bps)
        return {
            "signal": "YIELD_SPIKE_DETECTED",
            "expected_cascade": {
                "dxy": "UP (attracts USD)",
                "xauusd": "DOWN (USD stronger, gold weaker)",
                "usdjpy": "UP (yen carry unwind)"
            },
            "trade_setup": "SHORT_GOLD_LONG_DXY",
            "timing": "PRE_MARKET (before institutions move)"
        }
    return {"signal": "NORMAL"}