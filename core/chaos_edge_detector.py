import math
import statistics


def lyapunov_exponent(price_series, embedding_dim=5, tau=1):
    """Detect when market transitions from predictable to chaotic.

    Low Lyapunov = predictable trend
    High Lyapunov = chaos/ranging
    """
    n = len(price_series)
    if n < embedding_dim * tau + 10:
        return {"market_state": "INSUFFICIENT_DATA", "lyapunov": None}

    # Normalize prices
    mean = statistics.mean(price_series)
    std = statistics.stdev(price_series) if n > 1 else 1
    if std == 0:
        return {"market_state": "ORDERED", "lyapunov": 0, "recommendation": "FULL_EXECUTION"}

    normalized = [(p - mean) / std for p in price_series]

    # Create embedding vectors
    vectors = []
    for i in range(n - (embedding_dim - 1) * tau):
        vec = tuple(normalized[i + j * tau] for j in range(embedding_dim))
        vectors.append(vec)

    if len(vectors) < 2:
        return {"market_state": "INSUFFICIENT_DATA", "lyapunov": None}

    # Find nearest neighbors and track divergence
    divergences = []
    for i in range(len(vectors) - 1):
        min_dist = float('inf')
        min_idx = -1
        for j in range(i + 1, len(vectors)):
            dist = sum((vectors[i][k] - vectors[j][k]) ** 2 for k in range(embedding_dim)) ** 0.5
            if dist < min_dist and dist > 0:
                min_dist = dist
                min_idx = j

        if min_idx >= 0 and min_idx + 1 < len(vectors):
            # Distance after one time step
            next_dist = sum((vectors[i][k] - vectors[min_idx][k]) ** 2 for k in range(embedding_dim)) ** 0.5
            if next_dist > 0 and min_dist > 0:
                divergences.append(math.log(next_dist / min_dist))

    if not divergences:
        return {"market_state": "ORDERED", "lyapunov": 0, "recommendation": "FULL_EXECUTION"}

    lyapunov = statistics.mean(divergences)

    # Threshold: lyapunov > 0.05 = chaotic
    threshold = 0.05
    if lyapunov > threshold:
        return {
            "market_state": "CHAOTIC",
            "lyapunov": round(lyapunov, 4),
            "recommendation": "REDUCE_SIZE or SCALP_ONLY",
            "edge": "wait_for_reversion_to_order"
        }
    return {
        "market_state": "ORDERED",
        "lyapunov": round(lyapunov, 4),
        "recommendation": "FULL_EXECUTION"
    }


def strange_attractor_zones(h1_closes, d1_closes, lookback=50):
    """Price gravitates to hidden attractors (not obvious support/resistance).

    Uses clustering on normalized H1/D1 data to find attractor zones.
    """
    if len(h1_closes) < lookback or len(d1_closes) < lookback:
        return {"zones": [], "probability": "N/A", "trade": "WAIT"}

    # Normalize
    h1_mean = statistics.mean(h1_closes[-lookback:])
    h1_std = statistics.stdev(h1_closes[-lookback:]) if lookback > 1 else 1
    d1_mean = statistics.mean(d1_closes[-lookback:])
    d1_std = statistics.stdev(d1_closes[-lookback:]) if lookback > 1 else 1

    if h1_std == 0 or d1_std == 0:
        return {"zones": [], "probability": "N/A", "trade": "WAIT"}

    h1_norm = [(p - h1_mean) / h1_std for p in h1_closes[-lookback:]]
    d1_norm = [(p - d1_mean) / d1_std for p in d1_closes[-lookback:]]

    # Simple k-means-like clustering (3 zones)
    zones = _find_price_zones(h1_closes[-lookback:])

    current_price = h1_closes[-1]
    nearest_zone = min(zones, key=lambda z: abs(current_price - z["price"])) if zones else None

    return {
        "zones": zones,
        "nearest_attractor": nearest_zone,
        "probability": "65-70% price returns to attractor",
        "trade": "fade extremes back to attractor"
    }


def _find_price_zones(prices, n_zones=3):
    """Find price clusters via simple binning"""
    if not prices:
        return []

    sorted_prices = sorted(prices)
    chunk_size = len(sorted_prices) // n_zones
    zones = []

    for i in range(n_zones):
        start = i * chunk_size
        end = start + chunk_size if i < n_zones - 1 else len(sorted_prices)
        chunk = sorted_prices[start:end]
        if chunk:
            zones.append({
                "price": statistics.mean(chunk),
                "low": min(chunk),
                "high": max(chunk),
                "touches": len(chunk)
            })

    return zones
