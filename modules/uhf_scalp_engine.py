def tick_level_imbalance(bid_volumes, ask_volumes, lookback=5):
    """Sub-second order flow prediction"""
    if not bid_volumes or not ask_volumes:
        return None

    total_bids = sum(bid_volumes[-lookback:])
    total_asks = sum(ask_volumes[-lookback:])

    if total_asks == 0:
        return {"signal": "NO_ASK_LIQUIDITY", "trade": "WAIT"}

    bid_ask_ratio = total_bids / total_asks

    if bid_ask_ratio > 1.5:
        return {
            "signal": "NEXT_TICK_UP_70%_probability",
            "trade": "BUY_tick_collect_pip",
            "holding_time": "0.5_seconds",
            "bid_ask_ratio": round(bid_ask_ratio, 2)
        }
    elif bid_ask_ratio < 0.67:
        return {
            "signal": "NEXT_TICK_DOWN_70%_probability",
            "trade": "SELL_tick_collect_pip",
            "holding_time": "0.5_seconds",
            "bid_ask_ratio": round(bid_ask_ratio, 2)
        }

    return {
        "signal": "BALANCED",
        "trade": "WAIT",
        "bid_ask_ratio": round(bid_ask_ratio, 2)
    }


def liquidity_pool_depletion(pools, critical_level_pct=0.1):
    """DeFi liquidity about to dry up → price about to spike"""
    if not pools:
        return None

    alerts = []
    for pool in pools:
        name = pool.get("name", "unknown")
        balance = pool.get("balance", 0)
        avg_balance = pool.get("avg_balance", balance)
        tvl = pool.get("tvl", 0)

        if avg_balance > 0:
            depletion = 1 - (balance / avg_balance)
        elif tvl > 0:
            depletion = 1 - (balance / tvl)
        else:
            depletion = 0

        if depletion > critical_level_pct:
            alerts.append({
                "pool": name,
                "depletion_pct": round(depletion * 100, 1),
                "signal": "LIQUIDITY_SHOCK_INCOMING"
            })

    if alerts:
        return {
            "alerts": alerts,
            "expected_slippage": "high",
            "trade": "FADE_the_move_or_use_limit_orders"
        }

    return {"alerts": [], "signal": "NORMAL_LIQUIDITY"}
