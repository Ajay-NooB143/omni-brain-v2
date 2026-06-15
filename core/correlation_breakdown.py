def calculate_rolling_correlation(pair1_data, pair2_data, lookback=100):
    """Calculate rolling correlation between two price series"""
    if len(pair1_data) < lookback or len(pair2_data) < lookback:
        return 0
    
    p1 = pair1_data[-lookback:]
    p2 = pair2_data[-lookback:]
    
    mean1 = sum(p1) / len(p1)
    mean2 = sum(p2) / len(p2)
    
    num = sum((a - mean1) * (b - mean2) for a, b in zip(p1, p2))
    den1 = sum((a - mean1) ** 2 for a in p1) ** 0.5
    den2 = sum((b - mean2) ** 2 for b in p2) ** 0.5
    
    if den1 == 0 or den2 == 0:
        return 0
    return num / (den1 * den2)

def correlation_arbitrage(pair1_data, pair2_data, expected_correlation, lookback=100):
    """Alert when correlation deviates — reversion trade setup"""
    actual_corr = calculate_rolling_correlation(pair1_data, pair2_data, lookback)
    corr_deviation = abs(actual_corr - expected_correlation)
    
    if corr_deviation > 0.25:  # Significant breakdown
        return {
            "signal": "CORRELATION_BREAKDOWN",
            "expected": expected_correlation,
            "actual": actual_corr,
            "deviation": corr_deviation,
            "trade_setup": "REVERSION_PLAY",
            "target": expected_correlation
        }
    return {"signal": "NORMAL"}

# Example: XAUUSD vs DXY (normally -0.95)
# If corr becomes -0.70, gold/dollar decoupling → trade the reversion