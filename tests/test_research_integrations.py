import unittest

from modules.research_integrations import (
    check_optional_dependencies,
    create_finrl_stock_env,
    optimize_portfolio_weights,
    validate_finrl_market_data,
    validate_returns_matrix,
)


class ResearchIntegrationTests(unittest.TestCase):
    def test_dependency_check_reports_optional_packages_without_importing_them(self):
        status = check_optional_dependencies()
        self.assertIn("finrl", status)
        self.assertIn("riskfolio", status)
        self.assertIsInstance(status["finrl"], bool)
        self.assertIsInstance(status["riskfolio"], bool)

    def test_finrl_market_data_requires_ohlcv_and_identifiers(self):
        rows = [
            {"date": "2026-01-01", "tic": "XAUUSD", "open": 1, "high": 2,
             "low": 0.5, "close": 1.5, "volume": 100}
        ]
        with self.assertRaises(ValueError):
            validate_finrl_market_data(rows)

    def test_finrl_market_data_accepts_minimum_valid_history(self):
        rows = [
            {"date": "2026-01-01", "tic": "EURUSD", "open": 1, "high": 2,
             "low": 0.5, "close": 1.5, "volume": 100},
            {"date": "2026-01-02", "tic": "EURUSD", "open": 1.5, "high": 2,
             "low": 1, "close": 1.8, "volume": 120},
        ]
        self.assertEqual(validate_finrl_market_data(rows), rows)

    def test_finrl_market_data_rejects_missing_columns(self):
        with self.assertRaises(ValueError):
            validate_finrl_market_data([{"date": "2026-01-01", "close": 1}])

    def test_finrl_adapter_fails_clearly_when_dependency_is_missing(self):
        status = check_optional_dependencies()
        if not status["finrl"]:
            rows = [
                {"date": "2026-01-01", "tic": "AAPL", "open": 1, "high": 2,
                 "low": 0.5, "close": 1.5, "volume": 100},
                {"date": "2026-01-02", "tic": "AAPL", "open": 1.5, "high": 2,
                 "low": 1, "close": 1.8, "volume": 120},
            ]
            with self.assertRaisesRegex(RuntimeError, "FinRL is not installed"):
                create_finrl_stock_env(rows)

    def test_finrl_adapter_rejects_non_equity_asset_class(self):
        rows = [
            {"date": "2026-01-01", "tic": "XAUUSD", "open": 1, "high": 2,
             "low": 0.5, "close": 1.5, "volume": 100},
            {"date": "2026-01-02", "tic": "XAUUSD", "open": 1.5, "high": 2,
             "low": 1, "close": 1.8, "volume": 120},
        ]
        with self.assertRaises(ValueError):
            validate_finrl_market_data(rows, asset_class="commodity")

    def test_returns_matrix_requires_two_assets(self):
        with self.assertRaises(ValueError):
            validate_returns_matrix({"XAUUSD": [0.01, 0.02, -0.01]})

    def test_returns_matrix_requires_three_observations(self):
        with self.assertRaises(ValueError):
            validate_returns_matrix({
                "XAUUSD": [0.01, 0.02],
                "EURUSD": [0.02, 0.01],
            })

    def test_returns_matrix_rejects_non_finite_values(self):
        with self.assertRaises(ValueError):
            validate_returns_matrix({
                "XAUUSD": [0.01, float("nan"), 0.02],
                "EURUSD": [0.02, 0.01, 0.03],
            })

    def test_returns_matrix_accepts_equal_length_finite_series(self):
        result = validate_returns_matrix({
            "XAUUSD": [0.01, -0.02, 0.03],
            "EURUSD": [0.02, 0.01, -0.01],
        })
        self.assertEqual(result["assets"], ["XAUUSD", "EURUSD"])
        self.assertEqual(result["observations"], 3)

    def test_riskfolio_adapter_fails_clearly_when_dependency_is_missing(self):
        status = check_optional_dependencies()
        if not status["riskfolio"]:
            with self.assertRaisesRegex(RuntimeError, "Riskfolio-Lib is not installed"):
                optimize_portfolio_weights({
                    "XAUUSD": [0.01, -0.02, 0.03],
                    "EURUSD": [0.02, 0.01, -0.01],
                })


if __name__ == "__main__":
    unittest.main()
