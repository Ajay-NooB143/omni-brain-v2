class FractalModel:
    def predict(self, market_data, timeframe):
        return "HOLD"

    def update_accuracy(self, model_name, trade_result):
        if trade_result == "WIN":
            self.model_accuracy[model_name] = min(1.0, self.model_accuracy[model_name] + 0.05)
        else:
            self.model_accuracy[model_name] = max(0.0, self.model_accuracy[model_name] - 0.05)


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
