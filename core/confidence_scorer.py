def calculate_confidence(ob=0, fvg=0, sweep=0, vwap=0, session=0,
                         corr=0, yield_=0, sentiment=0, pattern=0, divergence=0):
    """Score 0-100 based on confluence factors"""
    score = 0
    score += min(ob * 15, 15)        # Order block: max 15
    score += min(fvg * 10, 10)       # FVG: max 10
    score += min(sweep * 10, 10)     # Sweep: max 10
    score += min(vwap * 10, 10)      # VWAP: max 10
    score += min(session * 5, 5)     # Session: max 5
    score += min(corr * 10, 10)      # Correlation: max 10
    score += min(yield_ * 10, 10)    # Yield: max 10
    score += min(sentiment * 10, 10) # Sentiment: max 10
    score += min(pattern * 10, 10)   # Pattern: max 10
    score += min(divergence * 10, 10)# Divergence: max 10
    return min(score, 100)


def get_signal(confidence):
    """Convert confidence score to signal verdict"""
    if confidence >= 75:
        return "EXECUTE"
    elif confidence >= 50:
        return "REFINE"
    else:
        return "BLOCK"
