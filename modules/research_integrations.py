"""Optional adapters for FinRL research and Riskfolio-Lib allocation analysis.

These adapters are deliberately isolated from the live execution path. They never
submit orders, change broker state, or size a live trade.
"""
from __future__ import annotations

import importlib.util
import math
from typing import Any, Mapping, Sequence


_FINRL_REQUIRED_COLUMNS = {"date", "tic", "open", "high", "low", "close", "volume"}


def check_optional_dependencies() -> dict[str, bool]:
    """Report whether optional research packages are import-discoverable."""
    return {
        "finrl": importlib.util.find_spec("finrl") is not None,
        "riskfolio": importlib.util.find_spec("riskfolio") is not None,
    }


def _records_and_columns(data: Any) -> tuple[list[dict[str, Any]], set[str]]:
    if hasattr(data, "columns") and hasattr(data, "to_dict"):
        columns = {str(column) for column in data.columns}
        records = data.to_dict(orient="records")
        return records, columns
    if not isinstance(data, Sequence) or isinstance(data, (str, bytes)):
        raise ValueError("Market data must be a sequence of row mappings or a DataFrame")
    records = list(data)
    if not records or not all(isinstance(row, Mapping) for row in records):
        raise ValueError("Market data must contain non-empty row mappings")
    columns = set().union(*(set(row.keys()) for row in records))
    return records, columns


def validate_finrl_market_data(data: Any, *, asset_class: str = "equity") -> Any:
    """Validate FinRL's date/ticker/OHLCV schema; intended for equity research only."""
    if asset_class.lower() != "equity":
        raise ValueError(
            "FinRL StockTradingEnv adapter is equity-research only; "
            "do not use it for FX, gold, CFDs, or live execution"
        )
    records, columns = _records_and_columns(data)
    missing = _FINRL_REQUIRED_COLUMNS - columns
    if missing:
        raise ValueError("FinRL market data is missing columns: " + ", ".join(sorted(missing)))
    if len(records) < 2:
        raise ValueError("FinRL market data requires at least two observations")
    for index, row in enumerate(records):
        for key in ("date", "tic"):
            if row.get(key) in (None, ""):
                raise ValueError(f"FinRL row {index} has an empty {key}")
        for key in ("open", "high", "low", "close", "volume"):
            try:
                value = float(row[key])
            except (TypeError, ValueError, KeyError):
                raise ValueError(f"FinRL row {index} has invalid {key}") from None
            if not math.isfinite(value):
                raise ValueError(f"FinRL row {index} has non-finite {key}")
            if key != "volume" and value <= 0:
                raise ValueError(f"FinRL row {index} has non-positive {key}")
            if key == "volume" and value < 0:
                raise ValueError(f"FinRL row {index} has negative volume")
    return data


def create_finrl_stock_env(data: Any, **env_kwargs: Any) -> Any:
    """Create FinRL's StockTradingEnv for validated equity data.

    This is a research/backtesting adapter only. It is not an order router.
    """
    validate_finrl_market_data(data, asset_class="equity")
    if importlib.util.find_spec("finrl") is None:
        raise RuntimeError(
            "FinRL is not installed. Install the optional research extra on a "
            "compatible research machine; do not add it to the live execution runtime."
        )
    try:
        import pandas as pd
        from finrl.meta.env_stock_trading.env_stocktrading import StockTradingEnv
    except ImportError as exc:
        raise RuntimeError(
            "FinRL StockTradingEnv requires pandas and the FinRL research dependencies"
        ) from exc
    frame = data if isinstance(data, pd.DataFrame) else pd.DataFrame(data)
    frame = frame.sort_values(["date", "tic"]).reset_index(drop=True)
    return StockTradingEnv(df=frame, **env_kwargs)


def validate_returns_matrix(returns: Mapping[str, Sequence[float]]) -> dict[str, Any]:
    """Validate aligned per-asset return series before portfolio optimization."""
    if not isinstance(returns, Mapping) or len(returns) < 2:
        raise ValueError("Portfolio optimization requires at least two assets")
    assets = list(returns.keys())
    lengths = set()
    for asset, series in returns.items():
        if not isinstance(asset, str) or not asset.strip():
            raise ValueError("Asset names must be non-empty strings")
        if isinstance(series, (str, bytes)) or not isinstance(series, Sequence):
            raise ValueError(f"Returns for {asset} must be a numeric sequence")
        lengths.add(len(series))
        for value in series:
            try:
                number = float(value)
            except (TypeError, ValueError):
                raise ValueError(f"Returns for {asset} must be numeric") from None
            if not math.isfinite(number):
                raise ValueError(f"Returns for {asset} must be finite")
    if len(lengths) != 1:
        raise ValueError("All assets must have the same number of observations")
    observations = lengths.pop()
    if observations < 3:
        raise ValueError("Portfolio optimization requires at least three observations")
    return {"assets": assets, "observations": observations}


def optimize_portfolio_weights(
    returns: Mapping[str, Sequence[float]],
    *,
    risk_measure: str = "MV",
    objective: str = "Sharpe",
    risk_free_rate: float = 0.0,
) -> dict[str, Any]:
    """Run optional Riskfolio-Lib mean-risk optimization; returns research weights only."""
    summary = validate_returns_matrix(returns)
    try:
        risk_free_rate = float(risk_free_rate)
    except (TypeError, ValueError):
        raise ValueError("risk_free_rate must be numeric") from None
    if not math.isfinite(risk_free_rate):
        raise ValueError("risk_free_rate must be finite")
    if importlib.util.find_spec("riskfolio") is None:
        raise RuntimeError(
            "Riskfolio-Lib is not installed. Install the optional research extra "
            "on a compatible research machine."
        )
    try:
        import pandas as pd
        import riskfolio as rp
    except ImportError as exc:
        raise RuntimeError("Riskfolio-Lib requires pandas and its declared dependencies") from exc

    returns_frame = pd.DataFrame(returns)
    portfolio = rp.Portfolio(returns=returns_frame)
    portfolio.assets_stats(method_mu="hist", method_cov="hist")
    weights_frame = portfolio.optimization(
        model="Classic",
        rm=risk_measure,
        obj=objective,
        rf=risk_free_rate,
        hist=True,
    )
    if weights_frame is None or "weights" not in weights_frame.columns:
        raise RuntimeError("Riskfolio-Lib did not return an optimized weights column")
    weights = {
        str(asset): float(weight)
        for asset, weight in weights_frame["weights"].items()
    }
    if not weights or not all(math.isfinite(weight) for weight in weights.values()):
        raise RuntimeError("Riskfolio-Lib returned invalid portfolio weights")
    return {
        "weights": weights,
        "assets": summary["assets"],
        "observations": summary["observations"],
        "risk_measure": risk_measure,
        "objective": objective,
        "mode": "RESEARCH_ONLY",
        "live_execution": False,
    }
