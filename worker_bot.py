import redis
import json
import os
from datetime import datetime

class WorkerBot:
    def __init__(self, worker_id, pairs, account_balance, redis_host='localhost', redis_port=6379):
        self.worker_id = worker_id
        self.pairs = pairs
        self.account_balance = account_balance
        self.redis = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        self.daily_pl = 0
        self.open_trades = 0
        self.exposure = 0
    
    def fetch_assigned_work(self):
        work_json = self.redis.rpop(f'queue:{self.worker_id}')
        if work_json:
            return json.loads(work_json)
        return None
    
    def execute_work(self, work, market_data):
        """Execute assigned work (placeholder for real trading logic)"""
        pair = work.get('pair')
        action = work.get('action')
        
        # Simulate execution
        result = {
            'work_id': work.get('work_id'),
            'pair': pair,
            'action': action,
            'status': 'EXECUTED',
            'timestamp': datetime.now().isoformat()
        }
        
        # Update local state
        if action == 'OPEN':
            self.open_trades += 1
            self.exposure += work.get('size', 0)
        elif action == 'CLOSE':
            self.open_trades = max(0, self.open_trades - 1)
            pnl = work.get('pnl', 0)
            self.daily_pl += pnl
            self.exposure = max(0, self.exposure - work.get('size', 0))
        
        # Update Redis
        self._update_status()
        
        return result
    
    def _update_status(self):
        self.redis.hset(f'worker:{self.worker_id}', mapping={
            'daily_pl': self.daily_pl,
            'open_trades': self.open_trades,
            'exposure': self.exposure,
            'status': 'ACTIVE',
            'last_update': datetime.now().isoformat()
        })
    
    def report_status(self):
        self._update_status()
        return {
            'worker_id': self.worker_id,
            'daily_pl': self.daily_pl,
            'open_trades': self.open_trades,
            'exposure': self.exposure
        }