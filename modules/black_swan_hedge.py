import statistics


def tail_risk_indicator(vix, put_skew, drawdown, correlation_extreme,
                         vix_threshold=25, skew_std_multiplier=2):
    """Detect when tail risk is high"""
    if vix <= 0 or put_skew <= 0:
        return None

    put_call_ratio = put_skew
    risk_factors = 0
    details = []

    if vix > vix_threshold:
        risk_factors += 1
        details.append(f"VIX={vix:.1f}>{vix_threshold}")

    if put_call_ratio > skew_std_multiplier:
        risk_factors += 1
        details.append(f"PUT_SKEW={put_call_ratio:.2f}>{skew_std_multiplier}")

    if drawdown > 15:
        risk_factors += 1
        details.append(f"DD={drawdown:.1f}%>15%")

    if correlation_extreme:
        risk_factors += 1
        details.append("CORR_EXTREME")

    if risk_factors >= 3:
        return {
            "tail_risk_level": "CRITICAL",
            "hedge": "BUY_OTM_puts or SHORT_index_futures",
            "cost": "1-2%_premium",
            "payoff": "10x if crash",
            "risk_factors": risk_factors,
            "details": details
        }
    elif risk_factors >= 2:
        return {
            "tail_risk_level": "ELEVATED",
            "hedge": "reduce_exposure_or_add_small_hedge",
            "risk_factors": risk_factors,
            "details": details
        }

    return {
        "tail_risk_level": "NORMAL",
        "hedge": "no_action_needed",
        "risk_factors": risk_factors
    }


def hedge_effectiveness_monitor(hedge_pnl, portfolio_pnl, hedge_cost):
    """Track hedge accuracy over time"""
    if hedge_cost <= 0:
        return {"feedback": "invalid_input"}

    net_hedge_pnl = hedge_pnl - hedge_cost
    protection_ratio = abs(hedge_pnl) / abs(portfolio_pnl) if portfolio_pnl != 0 else 0

    if net_hedge_pnl > 0 and protection_ratio > 0.5:
        return {
            "feedback": "keep_this_hedge_active",
            "net_hedge_pnl": round(net_hedge_pnl, 2),
            "protection_ratio": round(protection_ratio, 2),
            "next_rebalance": "quarterly"
        }
    elif net_hedge_pnl < 0:
        return {
            "feedback": "hedge_cost_exceeds_benefit",
            "net_hedge_pnl": round(net_hedge_pnl, 2),
            "recommendation": "reduce_hedge_size_or_switch_instruments"
        }

    return {
        "feedback": "hedge_neutral",
        "net_hedge_pnl": round(net_hedge_pnl, 2),
        "next_rebalance": "quarterly"
    }
