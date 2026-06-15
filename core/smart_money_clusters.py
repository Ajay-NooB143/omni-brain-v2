def identify_institutional_entries(order_blocks, volume_data, lookback_days=7):
    """Institutions enter on liquidity sweeps, not random spots"""
    if not order_blocks:
        return None

    results = []
    for ob in order_blocks:
        touches = ob.get("touches", 0)
        touch_window = ob.get("touch_window_days", 0)
        volume_increasing = ob.get("volume_trend", "flat") == "increasing"
        swept = ob.get("swept", False)

        if touches >= 3 and touch_window <= lookback_days:
            zone_type = "ACCUMULATION" if volume_increasing else "DISTRIBUTION"
            confidence = min(1.0, touches / lookback_days)

            results.append({
                "cluster": "INSTITUTIONAL_ZONE",
                "type": zone_type,
                "zone_high": ob.get("high"),
                "zone_low": ob.get("low"),
                "swept": swept,
                "touches": touches,
                "confidence": confidence,
                "next_target": ob.get("retest_level")
            })

    return results if results else None


def market_maker_traps(closes, highs, lows, round_levels, lookback=5):
    """MMs trap retail at round numbers before real move"""
    if len(closes) < lookback or not round_levels:
        return None

    current_price = closes[-1]
    avg_volume = sum(h - l for h, l in zip(highs[-lookback:], lows[-lookback:])) / lookback if lookback > 0 else 1

    for level in round_levels:
        distance = abs(current_price - level)
        near_round = distance < avg_volume * 0.1

        if near_round:
            # Check for stop hunt: price spiked through level then reversed
            prev_high = max(highs[-lookback:])
            prev_low = min(lows[-lookback:])
            swept_high = prev_high > level and current_price < level
            swept_low = prev_low < level and current_price > level

            if swept_high:
                return {
                    "trap_type": "ROUND_NUMBER_HUNT",
                    "level": level,
                    "likely_direction": "SELL",
                    "edge": "counter_trap",
                    "reason": "Swept highs above round level, now reversing"
                }
            elif swept_low:
                return {
                    "trap_type": "ROUND_NUMBER_HUNT",
                    "level": level,
                    "likely_direction": "BUY",
                    "edge": "counter_trap",
                    "reason": "Swept lows below round level, now reversing"
                }

    return None
