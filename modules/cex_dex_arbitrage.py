def spot_futures_basis_trade(spot_price, futures_price, funding_rate,
                              slippage_pct=0.001, min_spread_pct=0.005):
    """Futures premium → cash-and-carry trade"""
    if spot_price <= 0 or futures_price <= 0:
        return None

    basis = futures_price - spot_price
    basis_pct = basis / spot_price if spot_price > 0 else 0
    annualized_funding = funding_rate * 365

    if basis_pct > min_spread_pct and basis_pct > annualized_funding:
        profit_pct = basis_pct - (slippage_pct * 2)
        return {
            "trade": "SHORT_futures_LONG_spot",
            "basis": round(basis, 4),
            "basis_pct": round(basis_pct * 100, 3),
            "annualized_funding": round(annualized_funding * 100, 3),
            "profit_locked_pct": round(profit_pct * 100, 3),
            "risk": "execution_slippage"
        }

    return {"trade": "NO_ARB", "basis_pct": round(basis_pct * 100, 3)}


def dex_price_discovery_lag(dex_price, cex_price, slippage_cost=0.003,
                             min_profit_pct=0.002):
    """DEX lags CEX → arbitrage opportunity"""
    if dex_price <= 0 or cex_price <= 0:
        return None

    diff = abs(dex_price - cex_price)
    avg_price = (dex_price + cex_price) / 2
    diff_pct = diff / avg_price if avg_price > 0 else 0

    net_profit = diff_pct - (slippage_cost * 2)

    if net_profit > min_profit_pct:
        if dex_price < cex_price:
            return {
                "trade": "BUY_DEX_SELL_CEX",
                "dex_price": dex_price,
                "cex_price": cex_price,
                "profit_pct": round(net_profit * 100, 3)
            }
        else:
            return {
                "trade": "BUY_CEX_SELL_DEX",
                "dex_price": dex_price,
                "cex_price": cex_price,
                "profit_pct": round(net_profit * 100, 3)
            }

    return {"trade": "NO_ARB", "diff_pct": round(diff_pct * 100, 3)}
