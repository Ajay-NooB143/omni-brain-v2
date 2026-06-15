def volatility_skew_trade(atm_iv, otm_call_iv, otm_put_iv):
    """Options market predicts direction via skew"""
    if atm_iv <= 0 or otm_call_iv <= 0 or otm_put_iv <= 0:
        return None

    put_call_ratio = otm_put_iv / otm_call_iv if otm_call_iv > 0 else 0

    if put_call_ratio > 1.3:
        return {
            "signal": "PUT_SKEW_EXTREME",
            "interpretation": "market pricing in downside risk",
            "trade": "sell_puts_collect_premium or SHORT_directional",
            "put_call_ratio": round(put_call_ratio, 2)
        }
    elif otm_call_iv > otm_put_iv * 1.3:
        return {
            "signal": "CALL_SKEW_EXTREME",
            "interpretation": "market pricing in upside spike",
            "trade": "buy_calls or LONG_directional",
            "put_call_ratio": round(put_call_ratio, 2)
        }

    return {
        "signal": "SKEW_NORMAL",
        "interpretation": "no extreme directional bias",
        "trade": "WAIT",
        "put_call_ratio": round(put_call_ratio, 2)
    }


def volatility_term_structure(iv_30day, iv_90day, iv_180day):
    """Inverted term structure = reversal coming"""
    if iv_30day <= 0 or iv_90day <= 0 or iv_180day <= 0:
        return None

    if iv_30day > iv_90day > iv_180day:
        return {
            "structure": "INVERTED",
            "signal": "mean_reversion_incoming",
            "timeline": "7-14_days",
            "current_vix": iv_30day,
            "spread": round(iv_30day - iv_180day, 2)
        }
    elif iv_30day < iv_90day < iv_180day:
        return {
            "structure": "NORMAL",
            "signal": "contango_stable",
            "timeline": "no_urgent_reversal",
            "current_vix": iv_30day,
            "spread": round(iv_180day - iv_30day, 2)
        }

    return {
        "structure": "MIXED",
        "signal": "no_clear_structure",
        "trade": "WAIT",
        "current_vix": iv_30day
    }
