"""Multi-Timeframe Confirmation: D1 bias → H1 setup → M15 entry precision."""


def mtf_confirmation_full(d1_data, h1_data, m15_data, pair='EURUSD'):
    """
    Validate multi-timeframe confluence.

    D1 provides directional bias, H1 confirms setup, M15 pinpoints entry.

    Returns:
        dict: {
            'mtf_status': 'CONFIRMED' | 'PENDING' | 'REJECTED',
            'd1_bias': {'direction': 'BULLISH' | 'BEARISH' | 'NEUTRAL', 'strength': float},
            'h1_setup': {'valid': bool, 'pattern': str},
            'm15_entry': {'price': float, 'timing': str},
            'overall_confluence': float  # 0.0 - 1.0
        }
    """
    result = {
        'mtf_status': 'REJECTED',
        'd1_bias': {'direction': 'NEUTRAL', 'strength': 0.0},
        'h1_setup': {'valid': False, 'pattern': 'none'},
        'm15_entry': {'price': 0.0, 'timing': 'none'},
        'overall_confluence': 0.0,
    }

    if not d1_data or not h1_data or not m15_data:
        return result

    # --- D1: Directional Bias ---
    d1_close = d1_data.get('close', [])
    d1_structure = d1_data.get('structure', {})
    d1_trend = d1_structure.get('trend', 'neutral')

    if len(d1_close) >= 2:
        d1_direction = 'BULLISH' if d1_close[-1] > d1_close[0] else 'BEARISH'
        d1_strength = abs(d1_close[-1] - d1_close[0]) / d1_close[0] if d1_close[0] else 0
    else:
        d1_direction = 'BULLISH' if d1_trend == 'up' else ('BEARISH' if d1_trend == 'down' else 'NEUTRAL')
        d1_strength = 0.5 if d1_trend != 'neutral' else 0.0

    result['d1_bias'] = {'direction': d1_direction, 'strength': min(d1_strength * 100, 1.0)}

    if d1_direction == 'NEUTRAL':
        return result

    # --- H1: Setup Confirmation ---
    h1_close = h1_data.get('close', [])
    h1_structure = h1_data.get('structure', {})
    h1_trend = h1_structure.get('trend', 'neutral')
    order_block = h1_data.get('order_block', {})

    h1_aligned = (
        (d1_direction == 'BULLISH' and h1_trend == 'up')
        or (d1_direction == 'BEARISH' and h1_trend == 'down')
    )

    has_ob = bool(order_block.get('high') and order_block.get('low'))

    result['h1_setup'] = {
        'valid': h1_aligned and has_ob,
        'pattern': 'order_block' if has_ob else 'trend_align' if h1_aligned else 'none',
    }

    if not result['h1_setup']['valid']:
        return result

    # --- M15: Entry Precision ---
    m15_close = m15_data.get('close', [])
    m15_vwap = m15_data.get('vwap', [])

    if m15_close:
        entry_price = m15_close[-1]
        # Check if price is near VWAP (confluence)
        if m15_vwap:
            vwap_diff = abs(entry_price - m15_vwap[-1]) / entry_price
            timing = 'optimal' if vwap_diff < 0.001 else 'acceptable' if vwap_diff < 0.003 else 'late'
        else:
            timing = 'no_vwap'

        result['m15_entry'] = {'price': entry_price, 'timing': timing}
    else:
        return result

    # --- Overall Confluence ---
    confluence_parts = [
        result['d1_bias']['strength'],
        1.0 if result['h1_setup']['valid'] else 0.0,
        1.0 if timing in ('optimal', 'acceptable') else 0.5,
    ]
    result['overall_confluence'] = sum(confluence_parts) / len(confluence_parts)

    # --- Final Status ---
    if result['overall_confluence'] >= 0.6 and timing in ('optimal', 'acceptable'):
        result['mtf_status'] = 'CONFIRMED'
    elif result['overall_confluence'] >= 0.4:
        result['mtf_status'] = 'PENDING'
    else:
        result['mtf_status'] = 'REJECTED'

    return result
