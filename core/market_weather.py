def market_weather(atr, atr_sma, vix, news_impact, corr_stress):
    """Classify market regime"""
    volatility_ratio = atr / atr_sma
    if volatility_ratio > 2.0 or corr_stress > 0.85:
        return "STORMY"  # Reduce size, tighter stops
    elif news_impact > 0.7:
        return "FOGGY"   # Wait for clarity
    else:
        return "SUNNY"   # Full execution