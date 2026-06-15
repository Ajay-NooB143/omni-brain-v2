class AdaptiveThresholdLearner:
    def __init__(self, win_rate_target=0.60):
        self.execute_threshold = 75
        self.wait_threshold = 50
        self.block_threshold = 25
        self.win_rate_target = win_rate_target

    def update_thresholds(self, recent_trades):
        """If win rate < target, tighten thresholds"""
        if not recent_trades:
            return {"adjustment": "NONE", "reason": "no_trades"}

        wins = sum(1 for t in recent_trades if t.get('win'))
        recent_wr = wins / len(recent_trades)

        if recent_wr < self.win_rate_target:
            self.execute_threshold = min(100, self.execute_threshold + 2)
            self.wait_threshold = min(90, self.wait_threshold + 1)
            self.block_threshold = max(0, self.wait_threshold - 25)

            return {
                "adjustment": "TIGHTEN",
                "new_thresholds": {
                    "execute": self.execute_threshold,
                    "wait": self.wait_threshold,
                    "block": self.block_threshold
                },
                "reason": f"win_rate_{recent_wr:.2%}_below_target"
            }

        elif recent_wr > self.win_rate_target + 0.10:
            self.execute_threshold = max(50, self.execute_threshold - 1)
            self.wait_threshold = max(30, self.wait_threshold - 1)
            self.block_threshold = max(0, self.wait_threshold - 25)

            return {
                "adjustment": "LOOSEN",
                "new_thresholds": {
                    "execute": self.execute_threshold,
                    "wait": self.wait_threshold,
                    "block": self.block_threshold
                },
                "reason": "over_performing"
            }

        return {"adjustment": "NONE", "reason": "on_target"}

    def get_signal(self, confidence):
        """Return signal based on current adaptive thresholds"""
        if confidence >= self.execute_threshold:
            return "EXECUTE"
        elif confidence >= self.wait_threshold:
            return "REFINE"
        else:
            return "BLOCK"


def ensemble_weight_optimization(model_accuracy_history):
    """Automatically weight models by recent performance"""
    if not model_accuracy_history:
        return {}

    total_accuracy = sum(model_accuracy_history.values())
    if total_accuracy == 0:
        return {k: 1.0 / len(model_accuracy_history) for k in model_accuracy_history}

    weights = {}
    for model, accuracy in model_accuracy_history.items():
        weights[model] = round(accuracy / total_accuracy, 3)

    return weights
