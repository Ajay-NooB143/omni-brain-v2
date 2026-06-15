def find_local_lows(series):
    """Find local minima in price/RSI series"""
    lows = []
    for i in range(2, len(series) - 2):
        if series[i] < series[i-1] and series[i] < series[i-2] and series[i] < series[i+1] and series[i] < series[i+2]:
            lows.append(series[i])
    return lows

def calculate_divergence_magnitude(price_lows, rsi_lows):
    """Calculate divergence strength"""
    if len(price_lows) < 2 or len(rsi_lows) < 2:
        return 0
    price_change = abs(price_lows[-1] - price_lows[-2]) / price_lows[-2]
    rsi_change = abs(rsi_lows[-1] - rsi_lows[-2]) / rsi_lows[-2]
    return min(100, (price_change + rsi_change) * 50)

def hidden_order_flow(price_series, rsi_series, timeframe):
    """Detect institutional accumulation/distribution"""
    price_lows = find_local_lows(price_series)
    rsi_lows = find_local_lows(rsi_series)
    
    if len(price_lows) >= 2 and len(rsi_lows) >= 2:
        # Hidden bullish: price makes lower low, RSI makes higher low
        if price_lows[-1] < price_lows[-2] and rsi_lows[-1] > rsi_lows[-2]:
            return {
                "type": "HIDDEN_BULLISH_DIV",
                "strength": calculate_divergence_magnitude(price_lows, rsi_lows),
                "order_flow": "ACCUMULATION"
            }
        # Hidden bearish: price makes higher high, RSI makes lower high
        if price_lows[-1] > price_lows[-2] and rsi_lows[-1] < rsi_lows[-2]:
            return {
                "type": "HIDDEN_BEARISH_DIV",
                "strength": calculate_divergence_magnitude(price_lows, rsi_lows),
                "order_flow": "DISTRIBUTION"
            }
    return {"type": "NONE", "order_flow": "NEUTRAL"}