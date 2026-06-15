def calculate_dtw(pattern1, pattern2, band_width=10):
    """Dynamic Time Warping distance with Sakoe-Chiba band to bound memory"""
    n, m = len(pattern1), len(pattern2)
    dtw_matrix = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    dtw_matrix[0][0] = 0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if abs(i - j) > band_width:
                continue
            cost = abs(pattern1[i-1] - pattern2[j-1])
            dtw_matrix[i][j] = cost + min(
                dtw_matrix[i-1][j],    # insertion
                dtw_matrix[i][j-1],    # deletion
                dtw_matrix[i-1][j-1]   # match
            )
    return dtw_matrix[n][m]

def fractal_similarity(pattern_d1, pattern_h1, pattern_m15):
    """Self-similar patterns across timeframes"""
    d1_h1_match = calculate_dtw(pattern_d1, pattern_h1)
    h1_m15_match = calculate_dtw(pattern_h1, pattern_m15)
    fractal_score = (d1_h1_match * 0.6) + (h1_m15_match * 0.4)
    return max(0, min(100, 100 - fractal_score))  # 0-100, inverted so lower DTW = higher score

def predict_entry(d1_pattern, h1_data, m15_data):
    """If D1 shows ABC, predict H1 shows ABC → M15 entry"""
    score = fractal_similarity(d1_pattern, h1_data, m15_data)
    if score > 75:
        return {"prediction": "VALID_FRACTAL", "confidence": score}
    return {"prediction": "WAIT", "confidence": score}