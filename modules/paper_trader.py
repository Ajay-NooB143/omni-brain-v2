import json
from datetime import datetime
from redis_utils import get_redis_connection


def execute_paper_trade(pair, direction, entry, size, stop_loss, take_profit):
    """Log paper trade to Redis"""
    r = get_redis_connection()
    trade_id = f"paper-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    trade = {
        "trade_id": trade_id,
        "pair": pair,
        "direction": direction,
        "entry": entry,
        "size": size,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "status": "OPEN",
        "opened_at": datetime.now().isoformat()
    }
    r.lpush("paper_trades", json.dumps(trade))
    return trade_id
