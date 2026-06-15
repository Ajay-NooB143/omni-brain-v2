def generate_heatmap(positions, correlations=None, market_stress=0):
    """Visual: which positions are at risk, which safe"""
    if not positions:
        return {}

    correlations = correlations or {}
    heatmap = {}

    for pair, data in positions.items():
        exposure = data.get("exposure", 0)
        volatility = data.get("volatility", 0)
        drawdown = data.get("drawdown", 0)

        risk_score = exposure * 0.4 + volatility * 0.3 + drawdown * 0.3

        if risk_score > 0.7 or drawdown > 15:
            risk = "CRITICAL"
            color = "darkred"
        elif risk_score > 0.5:
            risk = "HIGH"
            color = "red"
        elif risk_score > 0.3:
            risk = "MEDIUM"
            color = "yellow"
        else:
            risk = "LOW"
            color = "green"

        # Correlation penalty
        for other_pair in correlations.get(pair, []):
            if other_pair in heatmap and heatmap[other_pair]["risk"] in ["HIGH", "CRITICAL"]:
                risk_score += 0.1
                if risk == "LOW":
                    risk = "MEDIUM"
                    color = "yellow"

        heatmap[pair] = {
            "exposure": round(exposure, 2),
            "risk_score": round(risk_score, 2),
            "risk": risk,
            "color": color
        }

    if market_stress > 0.85:
        heatmap["WARNING"] = "diversification_breaking_down"

    return heatmap
