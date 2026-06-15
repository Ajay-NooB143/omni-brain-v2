import numpy as np


def calculate_rolling_correlation(pair1_data, pair2_data, lookback=100):
    """Calculate rolling correlation between two price series"""
    if len(pair1_data) < lookback or len(pair2_data) < lookback:
        return None

    p1 = np.array(pair1_data[-lookback:], dtype=float)
    p2 = np.array(pair2_data[-lookback:], dtype=float)

    valid_idx = ~(np.isnan(p1) | np.isnan(p2))
    if valid_idx.sum() < 30:
        return None

    p1_clean = p1[valid_idx]
    p2_clean = p2[valid_idx]

    current_corr = np.corrcoef(p1_clean, p2_clean)[0, 1]
    if np.isnan(current_corr):
        return None
    return float(current_corr)


def correlation_arbitrage(pair1_data, pair2_data, expected_correlation, lookback=100):
    """Alert when correlation deviates — reversion trade setup"""
    actual_corr = calculate_rolling_correlation(pair1_data, pair2_data, lookback)
    if actual_corr is None:
        return {"signal": "NORMAL", "reason": "Insufficient valid data"}

    corr_deviation = abs(actual_corr - expected_correlation)

    if corr_deviation > 0.25:
        return {
            "signal": "CORRELATION_BREAKDOWN",
            "expected": expected_correlation,
            "actual": actual_corr,
            "deviation": corr_deviation,
            "trade_setup": "REVERSION_PLAY",
            "target": expected_correlation
        }
    return {"signal": "NORMAL"}
