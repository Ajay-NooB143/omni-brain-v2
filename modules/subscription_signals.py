def vip_signal_package(setup, subscription_tier):
    """Tier-based signal delivery"""
    base_signal = {
        "pair": setup['pair'],
        "entry": setup['entry_price'],
        "verdict": setup['verdict']
    }
    
    max_leverage = 2.0
    
    if subscription_tier == "VIP":
        multiplier = min(2.0, max_leverage)
        return {
            **base_signal,
            "priority": "EARLY_ACCESS",
            "delay": 0,  # Sent immediately
            "position_size": setup['size'] * multiplier,
            "extras": [
                "correlation_alerts",
                "custom_pair_tracking",
                "divergence_scanner",
                "yield_arbitrage_radar"
            ]
        }
    elif subscription_tier == "PRO":
        multiplier = min(1.5, max_leverage)
        return {
            **base_signal,
            "delay": 15 * 60,  # 15min delay
            "position_size": setup['size'] * multiplier,
            "extras": ["yield_arbitrage_radar"]
        }
    else:  # FREE
        return {
            **base_signal,
            "delay": 30 * 60,  # 30min delay
            "position_size": setup['size'],
            "extras": []
        }