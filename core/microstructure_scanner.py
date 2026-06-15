import statistics


def detect_iceberg_orders(bid_ask_spreads, volumes, lookback=20):
    """Identify hidden institutional orders via spread + volume analysis"""
    if len(bid_ask_spreads) < lookback or len(volumes) < lookback:
        return None

    recent_spreads = bid_ask_spreads[-lookback:]
    recent_volumes = volumes[-lookback:]

    normal_spread = statistics.mean(recent_spreads)
    current_spread = bid_ask_spreads[-1]
    current_volume = volumes[-1]
    avg_volume = statistics.mean(recent_volumes)

    # Tight spread + volume spike that vanishes = iceberg
    if current_spread < normal_spread * 0.5:
        if current_volume > avg_volume * 2:
            # Check if next candle volume drops (vanish pattern)
            if len(volumes) > lookback and volumes[-2] < avg_volume * 0.8:
                return {
                    "pattern": "ICEBERG_ORDER",
                    "institution": "likely",
                    "direction": "buy_if_volume_on_bid_side",
                    "edge": "front_run_iceberg",
                    "spread_ratio": current_spread / normal_spread if normal_spread > 0 else 0,
                    "volume_ratio": current_volume / avg_volume if avg_volume > 0 else 0
                }

    return None


def order_flow_imbalance(cumulative_deltas, price_closes, lookback=20):
    """Buy vs sell volume imbalance = direction predictor"""
    if len(cumulative_deltas) < lookback or len(price_closes) < lookback:
        return None

    recent_deltas = cumulative_deltas[-lookback:]
    recent_closes = price_closes[-lookback:]

    mean_delta = statistics.mean(recent_deltas)
    std_delta = statistics.stdev(recent_deltas) if len(recent_deltas) > 1 else 1
    max_delta = max(abs(d) for d in recent_deltas) if recent_deltas else 1

    current_delta = cumulative_deltas[-1]
    price_trending_up = recent_closes[-1] > recent_closes[-5] if len(recent_closes) >= 5 else False

    z_score = (current_delta - mean_delta) / std_delta if std_delta > 0 else 0

    if abs(z_score) > 2:
        if z_score > 0 and price_trending_up:
            return {
                "signal": "STRONG_BUY_ACCUMULATION",
                "confidence": min(1.0, abs(z_score) / 4),
                "z_score": z_score
            }
        elif z_score < 0 and not price_trending_up:
            return {
                "signal": "STRONG_SELL_DISTRIBUTION",
                "confidence": min(1.0, abs(z_score) / 4),
                "z_score": z_score
            }

    return {"signal": "NEUTRAL", "confidence": 0, "z_score": z_score}
