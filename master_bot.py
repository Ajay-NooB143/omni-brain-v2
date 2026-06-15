import redis
import json
import time
from datetime import datetime

class MasterOrchestrator:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.workers = {}
    
    def register_worker(self, worker_id, pairs, account_allocation, max_daily_loss=2.0):
        worker_data = {
            'worker_id': worker_id,
            'pairs': pairs,
            'account': account_allocation,
            'max_daily_loss': max_daily_loss,
            'registered_at': datetime.now().isoformat(),
            'status': 'ACTIVE'
        }
        self.redis.hset(f'worker:{worker_id}', mapping=worker_data)
        self.redis.sadd('workers:active', worker_id)
        return worker_data
    
    def get_cluster_status(self):
        workers = self.redis.smembers('workers:active')
        health = {}
        total_daily_pl = 0
        total_exposure = 0
        
        for worker_id in workers:
            data = self.redis.hgetall(f'worker:{worker_id}')
            if data:
                daily_pl = float(data.get('daily_pl', 0))
                trades = int(data.get('open_trades', 0))
                exposure = float(data.get('exposure', 0))
                
                health[worker_id] = {
                    'status': data.get('status', 'UNKNOWN'),
                    'trades': trades,
                    'daily_pl': daily_pl
                }
                total_daily_pl += daily_pl
                total_exposure += exposure
        
        # Circuit breaker logic
        loss_percent = abs(total_daily_pl) / 10000 * 100  # Assuming 10k total account
        circuit_breaker = 'ON' if loss_percent > 5.0 else 'OFF'
        
        triggered_workers = []
        for worker_id in workers:
            data = self.redis.hgetall(f'worker:{worker_id}')
            if data:
                w_loss = abs(float(data.get('daily_pl', 0))) / float(data.get('account', 3333)) * 100
                if w_loss > 2.0:
                    triggered_workers.append({
                        'worker_id': worker_id,
                        'loss_percent': w_loss
                    })
        
        return {
            'health': {
                'cluster_status': 'HEALTHY' if circuit_breaker == 'OFF' else 'CIRCUIT_BREAKER',
                'workers': health
            },
            'risk': {
                'total_exposure': total_exposure,
                'exposure_percent': total_exposure / 10000 * 100,
                'max_drawdown': loss_percent,
                'loss_percent': loss_percent
            },
            'circuit_breaker': {
                'circuit_breaker': circuit_breaker,
                'triggered_workers': triggered_workers
            },
            'total_daily_pl': total_daily_pl
        }
    
    def assign_work(self, worker_id, work_data):
        self.redis.lpush(f'queue:{worker_id}', json.dumps(work_data))

class AuditSystem:
    def __init__(self, redis_host='localhost', redis_port=6379):
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
    
    def log_worker_status(self, data):
        data['timestamp'] = datetime.now().isoformat()
        self.redis.lpush('audit:worker_status', json.dumps(data))
        self.redis.ltrim('audit:worker_status', 0, 9999)
    
    def log_circuit_breaker(self, data):
        data['timestamp'] = datetime.now().isoformat()
        self.redis.lpush('audit:circuit_breaker', json.dumps(data))
    
    def get_compliance_report(self, start_date, end_date):
        # Simplified - in production would filter by date
        return {
            'period': f"{start_date} to {end_date}",
            'total_trades': self.redis.llen('audit:trades_opened'),
            'circuit_breakers': self.redis.llen('audit:circuit_breaker'),
            'status': 'COMPLIANT'
        }
    
    def export_audit_csv(self, event_type, filepath):
        with open(filepath, 'w') as f:
            f.write("timestamp,event,data\n")
            events = self.redis.lrange(f'audit:{event_type.lower()}', 0, -1)
            for event in events:
                f.write(f"{event}\n")