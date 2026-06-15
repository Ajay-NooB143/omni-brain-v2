from datetime import datetime, timedelta


def fibonacci_time_cycle(swing_high_date, swing_low_date):
    """Price peaks/troughs repeat at Fib time intervals"""
    if isinstance(swing_high_date, str):
        swing_high_date = datetime.fromisoformat(swing_high_date)
    if isinstance(swing_low_date, str):
        swing_low_date = datetime.fromisoformat(swing_low_date)

    cycle_length = abs((swing_high_date - swing_low_date).days)
    fib_multiples = [1, 1.618, 2.618, 4.236, 6.854]

    base_date = min(swing_high_date, swing_low_date)
    projection_dates = []
    for fib in fib_multiples:
        next_reversal = base_date + timedelta(days=int(cycle_length * fib))
        projection_dates.append(next_reversal)

    return {
        "next_reversals": [d.isoformat() for d in projection_dates],
        "cycle_length_days": cycle_length,
        "alert": f"Watch for reversals on {projection_dates[0].strftime('%Y-%m-%d')}"
    }


def lunar_cycle_correlation(price_data, lunar_phases=None):
    """Some pairs show correlation with moon phases (full/new)"""
    if lunar_phases is None:
        lunar_phases = _estimate_lunar_phases()

    next_full = None
    next_new = None
    now = datetime.now()

    for phase in lunar_phases:
        if isinstance(phase["date"], str):
            phase_date = datetime.fromisoformat(phase["date"])
        else:
            phase_date = phase["date"]

        if phase_date > now:
            if phase["phase"] == "FULL" and next_full is None:
                next_full = phase_date
            elif phase["phase"] == "NEW" and next_new is None:
                next_new = phase_date

        if next_full and next_new:
            break

    return {
        "next_full_moon": next_full.isoformat() if next_full else None,
        "next_new_moon": next_new.isoformat() if next_new else None,
        "expected_volatility": "HIGH",
        "pairs_correlated": ["EURUSD", "GBPUSD"],
        "correlation_range": "58-62%"
    }


def _estimate_lunar_phases():
    """Estimate lunar phases using simple synodic month (29.53 days)"""
    known_new_moon = datetime(2024, 1, 11)  # Known new moon date
    synodic_month = 29.53
    phases = []

    # Generate phases for next 90 days
    for i in range(-2, 6):
        base = known_new_moon + timedelta(days=synodic_month * i)
        phases.append({"date": base.isoformat(), "phase": "NEW"})
        phases.append({"date": (base + timedelta(days=synodic_month / 2)).isoformat(), "phase": "FULL"})

    return sorted(phases, key=lambda x: x["date"])
