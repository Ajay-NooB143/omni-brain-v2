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

def calculate_position_size(account_balance, risk_percent, entry_price, stop_loss):
    """Calculate position size based on risk parameters."""
    risk_amount = account_balance * (risk_percent / 100)
    sl_distance = abs(entry_price - stop_loss) if stop_loss else entry_price * 0.01

    if sl_distance == 0:
        lots = 0.0
    else:
        # Standard lot = 100,000 units; value per pip varies by pair
        pip_value = sl_distance * 100  # simplified
        lots = round(risk_amount / max(pip_value, 1), 2)

    return {
        'lots': max(lots, 0.01),
        'risk_amount': round(risk_amount, 2),
        'sl_distance': round(sl_distance, 5),
    }

def calculate_stop_loss(entry_price, direction, sl_pips=50):
    """Calculate stop loss price."""
    pip_size = 0.0001  # For forex; adjust for JPY/crypto
    if direction == 'LONG':
        return round(entry_price - (sl_pips * pip_size), 5)
    else:
        return round(entry_price + (sl_pips * pip_size), 5)

def calculate_take_profit(entry_price, direction, tp_pips=100):
    """Calculate take profit price."""
    pip_size = 0.0001
    if direction == 'LONG':
        return round(entry_price + (tp_pips * pip_size), 5)
    else:
        return round(entry_price - (tp_pips * pip_size), 5)

def calculate_dynamic_grid(confidence, market_weather, account_risk, portfolio_dd):
    """Adaptive position sizing + grid."""
    base_size = account_risk * 0.02  # 2% risk per trade

    if market_weather == "STORMY":
        size_multiplier = 0.5
        grid_levels = 2
        grid_spacing = "wide"
        action = "EXECUTE"
    elif market_weather == "FOGGY":
        return {"action": "BLOCK", "reason": "Wait for clarity", "grid_levels": 0, "grid_spacing": "none"}
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
            return {"action": "BLOCK", "reason": "Low confidence", "grid_levels": 0, "grid_spacing": "none"}
        action = "EXECUTE"

    position_size = base_size * size_multiplier
    return {
        "action": action,
        "size": position_size,
        "grid_levels": grid_levels,
        "grid_spacing": grid_spacing,
        "stops": calculate_stops(position_size),
    }

# Keep old name as alias
dynamic_grid = calculate_dynamic_grid