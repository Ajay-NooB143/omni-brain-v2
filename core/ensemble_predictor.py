import logging

from core.fractal_prediction import calculate_dtw

logger = logging.getLogger(__name__)


class FractalModel:
    def __init__(self):
        self.min_pattern_len = 15

    def predict(self, market_data, timeframe):
        closes = self._extract_closes(market_data)
        if len(closes) < self.min_pattern_len:
            return "HOLD"

        half = len(closes) // 2
        recent = closes[-half:]
        earlier = closes[:half]

        similarity = max(0, 100 - calculate_dtw(recent, earlier))

        if similarity > 70:
            return "BUY" if recent[-1] > recent[0] else "SELL"
        return "HOLD"

    @staticmethod
    def _extract_closes(market_data):
        if isinstance(market_data, dict):
            return market_data.get("close", [])
        if isinstance(market_data, list):
            return market_data
        return []


class LiquidityModel:
    def predict(self, market_data, timeframe):
        return "HOLD"


class CycleModel:
    def predict(self, market_data, timeframe):
        return "HOLD"


class SentimentModel:
    def predict(self, market_data, timeframe):
        return "HOLD"


class NeuralModel:
    def predict(self, market_data, timeframe):
        return "HOLD"


class EnsembleVoting:
    def __init__(self):
        self.models = {
            "fractal": FractalModel(),
            "liquidity": LiquidityModel(),
            "cycle": CycleModel(),
            "sentiment": SentimentModel(),
            "neural": NeuralModel()
        }
        self.model_accuracy = {k: 0.5 for k in self.models}

    def predict(self, market_data, timeframe):
        """5 models vote, weighted by recent accuracy"""
        votes = {}

        for model_name, model in self.models.items():
            prediction = model.predict(market_data, timeframe)
            weight = self.model_accuracy[model_name]
            votes[model_name] = {
                "prediction": prediction,
                "weight": weight
            }

        buy_votes = sum(v["weight"] for v in votes.values() if v["prediction"] == "BUY")
        sell_votes = sum(v["weight"] for v in votes.values() if v["prediction"] == "SELL")

        consensus = buy_votes / (buy_votes + sell_votes) if (buy_votes + sell_votes) > 0 else 0.5

        if consensus > 0.7:
            return {"verdict": "STRONG_BUY", "consensus": consensus}
        elif consensus > 0.6:
            return {"verdict": "BUY", "consensus": consensus}
        elif consensus < 0.3:
            return {"verdict": "STRONG_SELL", "consensus": consensus}
        elif consensus < 0.4:
            return {"verdict": "SELL", "consensus": consensus}
        else:
            return {"verdict": "DIVERGENCE_WAIT", "consensus": consensus}

    def update_accuracy(self, model_name, trade_result):
        """After trade closes, update model accuracy"""
        if model_name not in self.model_accuracy:
            return
        if trade_result == "WIN":
            self.model_accuracy[model_name] = min(1.0, self.model_accuracy[model_name] + 0.05)
        else:
            self.model_accuracy[model_name] = max(0.0, self.model_accuracy[model_name] - 0.05)
