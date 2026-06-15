import json
from datetime import datetime
from redis_utils import get_redis_connection


class AuditSystem:
    def __init__(self, redis_host=None, redis_port=None):
        self.redis = get_redis_connection(redis_host, redis_port)

    def log_worker_status(self, data):
        data['timestamp'] = datetime.now().isoformat()
        self.redis.lpush('audit:worker_status', json.dumps(data))
        self.redis.ltrim('audit:worker_status', 0, 9999)

    def log_circuit_breaker(self, data):
        data['timestamp'] = datetime.now().isoformat()
        self.redis.lpush('audit:circuit_breaker', json.dumps(data))
        self.redis.ltrim('audit:circuit_breaker', 0, 9999)

    def log_trade(self, event_type, trade_data):
        trade_data['timestamp'] = datetime.now().isoformat()
        trade_data['event'] = event_type
        self.redis.lpush(f'audit:{event_type.lower()}', json.dumps(trade_data))

    def get_compliance_report(self, start_date, end_date):
        return {
            'period': f"{start_date} to {end_date}",
            'total_trades_opened': self.redis.llen('audit:trade_opened'),
            'total_trades_closed': self.redis.llen('audit:trade_closed'),
            'circuit_breakers': self.redis.llen('audit:circuit_breaker'),
            'worker_status_logs': self.redis.llen('audit:worker_status'),
            'status': 'COMPLIANT'
        }

    def export_audit_csv(self, event_type, filepath):
        events = self.redis.lrange(f'audit:{event_type.lower()}', 0, -1)
        with open(filepath, 'w') as f:
            f.write("timestamp,event,data\n")
            for event in events:
                try:
                    data = json.loads(event)
                    f.write(f"{data.get('timestamp', '')},{data.get('event', '')},{json.dumps(data)}\n")
                except Exception:
                    f.write(f",,{event}\n")
