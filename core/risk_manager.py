def validate_stops(sl_pips):
    """Ensure stop loss is valid"""
    if sl_pips <= 0:
        raise ValueError("Stop loss must be > 0 pips")
    return sl_pips

def calculate_stops(position_size):
    """Calculate stop loss levels"""
    sl = 20 * (position_size / 1000)
    tp = 40 * (position_size / 1000)
    validate_stops(sl)
    return {
        "sl_pips": sl,
        "tp_pips": tp
    }

def dynamic_grid(confidence, market_weather, account_risk, portfolio_dd):
    """Adaptive position sizing + grid"""
    base_size = account_risk * 0.02  # 2% risk per trade
    
    if market_weather == "STORMY":
        size_multiplier = 0.5
        grid_levels = 2
        grid_spacing = "wide"
    elif market_weather == "FOGGY":
        return {"action": "BLOCK", "reason": "Wait for clarity"}
    else:  # SUNNY
        if confidence >= 80:
            size_multiplier = 1.5
            grid_levels = 5
            grid_spacing = "tight"
        elif confidence >= 50:
            size_multiplier = 1.0
            grid_levels = 3
            grid_spacing = "medium"
        else:
            return {"action": "BLOCK", "reason": "Low confidence"}
    
    position_size = base_size * size_multiplier
    return {
        "size": position_size,
        "grid_levels": grid_levels,
        "grid_spacing": grid_spacing,
        "stops": calculate_stops(position_size)
    }