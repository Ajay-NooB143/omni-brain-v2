# Research Integrations (FinRL + Riskfolio-Lib)

This integration layer adds optional research tools without changing the existing live/paper execution modules.

## Why these projects

- **FinRL** is a reinforcement-learning research framework. Its StockTradingEnv adapter is explicitly equity-only here; it is not the gold/FX execution engine and must not be used to route orders.
- **Riskfolio-Lib** provides portfolio optimization and risk models. It can calculate research allocation weights from aligned historical returns; the returned weights are not broker orders and do not override the existing risk manager.

The shared Gemini list also included Nansen CLI, Timefold, GPT trading bot, Trading Gym and other projects. They are not wired into the core:
- Nansen CLI is primarily on-chain/crypto intelligence and does not directly add a verified XAUUSD/FX signal.
- Timefold is a Java/Kotlin planning solver, not a market forecasting or execution engine.
- The GPT/Indodax bot is exchange-specific and is not suitable as a broker execution adapter.
- Trading Gym / FinRL overlap as RL research environments; FinRL was selected as the more mature research framework for this phase.
- Riskfolio-Lib was selected for portfolio-level risk/allocation analysis.

## Optional installation

Install only on a separate research machine/virtual environment that supports the dependencies:

    pip install -e ".[research]"

The core requirements do not install FinRL or Riskfolio-Lib.

## API

    from modules.research_integrations import (
        check_optional_dependencies,
        create_finrl_stock_env,
        optimize_portfolio_weights,
    )

    print(check_optional_dependencies())

    # Equity OHLCV data only. This creates a research environment, not a live broker.
    env = create_finrl_stock_env(equity_dataframe, stock_dim=..., hmax=...)

    # Aligned historical returns, one series per asset.
    result = optimize_portfolio_weights({
        "XAUUSD": gold_returns,
        "EURUSD": eurusd_returns,
        "GBPUSD": gbpusd_returns,
    })
    print(result["weights"])
    assert result["live_execution"] is False

## Safety and validation

- Both packages are optional and imported lazily.
- FinRL input requires date/tic/open/high/low/close/volume columns and at least two rows.
- The FinRL StockTradingEnv wrapper rejects non-equity asset classes. Do not pass gold, FX, CFDs or crypto to this equity adapter.
- Riskfolio-Lib requires at least two assets, three aligned observations, and finite numeric returns.
- Optimization output is marked RESEARCH_ONLY; it is not connected to order placement or automatic position sizing.
- Backtest and paper-trade any research output. Never treat model weights or simulated returns as a guarantee of future performance.

## Current environment note

The current Android/Termux Ubuntu ARM64 environment does not have NumPy, pandas, pytest, FinRL or Riskfolio-Lib installed. The adapter validation tests use Python's standard library and can run without those optional packages. Install the research extra only after checking compatibility on the intended PC/VPS.
