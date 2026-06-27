"""Correlation analysis engine for forex pairs."""


def pair_correlation(pair):
    """Placeholder: return correlation strength 0-1."""
    return 0.5


def detect_correlation_breakdown(pair_a_data, pair_b_data, expected_corr=0.85, threshold=0.25):
    """
    Detect correlation breakdown between two correlated pairs.

    When correlation deviates significantly from expected, an arbitrage
    opportunity may exist.

    Returns:
        dict: {
            'breakdown': bool,
            'current_corr': float,
            'expected_corr': float,
            'deviation': float,
            'trade_signal': str | None,
            'description': str
        }
    """
    result = {
        'breakdown': False,
        'current_corr': 0.0,
        'expected_corr': expected_corr,
        'deviation': 0.0,
        'trade_signal': None,
        'description': 'No data',
    }

    if not pair_a_data or not pair_b_data:
        return result

    closes_a = pair_a_data.get('close', [])
    closes_b = pair_b_data.get('close', [])

    if len(closes_a) < 5 or len(closes_b) < 5:
        result['description'] = 'Insufficient data points'
        return result

    # Use last N points for correlation
    n = min(len(closes_a), len(closes_b))
    a = closes_a[-n:]
    b = closes_b[-n:]

    # Calculate returns
    returns_a = [(a[i] - a[i - 1]) / a[i - 1] for i in range(1, len(a)) if a[i - 1] != 0]
    returns_b = [(b[i] - b[i - 1]) / b[i - 1] for i in range(1, len(b)) if b[i - 1] != 0]

    if len(returns_a) < 3 or len(returns_b) < 3:
        result['description'] = 'Insufficient return data'
        return result

    # Pearson correlation
    n = min(len(returns_a), len(returns_b))
    ra = returns_a[:n]
    rb = returns_b[:n]

    mean_a = sum(ra) / n
    mean_b = sum(rb) / n

    cov = sum((ra[i] - mean_a) * (rb[i] - mean_b) for i in range(n)) / n
    std_a = (sum((x - mean_a) ** 2 for x in ra) / n) ** 0.5
    std_b = (sum((x - mean_b) ** 2 for x in rb) / n) ** 0.5

    if std_a == 0 or std_b == 0:
        result['description'] = 'Zero variance in returns'
        return result

    current_corr = cov / (std_a * std_b)
    deviation = abs(current_corr - expected_corr)

    result['current_corr'] = round(current_corr, 4)
    result['deviation'] = round(deviation, 4)

    if deviation > threshold:
        result['breakdown'] = True
        result['description'] = f'Correlation breakdown: {current_corr:.2f} vs expected {expected_corr:.2f}'

        # Simple arbitrage signal
        if current_corr < expected_corr - threshold:
            result['trade_signal'] = 'CONVERGENCE_LONG'
        else:
            result['trade_signal'] = 'CONVERGENCE_SHORT'
    else:
        result['description'] = f'Correlation normal: {current_corr:.2f}'

    return result
