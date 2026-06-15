def optimal_rebalance_after_dd(portfolio_dd, equity_curve=None, volatility=0):
    """When underwater, add capital strategically"""
    if portfolio_dd <= 0:
        return {"strategy": "NO_DRAWDOWN", "action": "HOLD"}

    if portfolio_dd > 30:
        return {
            "strategy": "AGGRESSIVE_ENTRY",
            "tranches": [
                {"at_dd": 30, "add": "25%_capital"},
                {"at_dd": 35, "add": "30%_capital"},
                {"at_dd": 40, "add": "45%_capital"}
            ],
            "rationale": "deep_drawdown_max_opportunity"
        }

    if portfolio_dd > 20:
        return {
            "strategy": "SCALED_ENTRY",
            "tranches": [
                {"at_dd": 20, "add": "10%_capital"},
                {"at_dd": 25, "add": "15%_capital"},
                {"at_dd": 30, "add": "25%_capital"}
            ],
            "rationale": "buy_dip_lower_than_previous"
        }

    if portfolio_dd > 10:
        return {
            "strategy": "LIGHT_ENTRY",
            "tranches": [
                {"at_dd": 10, "add": "5%_capital"},
                {"at_dd": 15, "add": "10%_capital"}
            ],
            "rationale": "minor_drawdown_caution"
        }

    return {"strategy": "NORMAL", "action": "full_position_sizing"}


def volatility_adjusted_position_sizing(current_vol, avg_vol, account_risk_pct,
                                         account_balance, atr, pair="UNKNOWN"):
    """Higher vol → smaller size"""
    if current_vol <= 0 or avg_vol <= 0 or atr <= 0:
        return {"adjusted_lots": 0, "reason": "invalid_input"}

    vol_ratio = current_vol / avg_vol
    risk_amount = account_balance * (account_risk_pct / 100)
    base_size = risk_amount / atr

    adjusted_size = base_size / vol_ratio

    return {
        "pair": pair,
        "vol_ratio": round(vol_ratio, 3),
        "base_lots": round(base_size, 4),
        "adjusted_lots": round(adjusted_size, 4),
        "risk_amount": round(risk_amount, 2),
        "reason": "protect_on_high_vol_days" if vol_ratio > 1.5 else "normal_sizing"
    }
