import redis
import json
import os
from datetime import datetime
from redis_utils import get_redis_connection

class WorkerBot:
    def __init__(self, worker_id, pairs, account_balance, redis_host=None, redis_port=None):
        self.worker_id = worker_id
        self.pairs = pairs
        self.account_balance = account_balance
        self.redis = get_redis_connection(redis_host, redis_port)
        self.daily_pl = 0
        self.open_trades = 0
        self.exposure = 0

    def fetch_assigned_work(self, timeout=5):
        """Blocking pop with timeout instead of busy-wait RPOP"""
        result = self.redis.blpop(f'queue:{self.worker_id}', timeout=timeout)
        if result:
            _, work_json = result
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
            # Log trade open
            self._log_audit('trades_opened', {
                'worker_id': self.worker_id,
                'pair': pair,
                'direction': work.get('direction'),
                'size': work.get('size'),
                'entry': work.get('entry'),
                'confidence': work.get('confidence')
            })
        elif action == 'CLOSE':
            self.open_trades = max(0, self.open_trades - 1)
            pnl = work.get('pnl', 0)
            self.daily_pl += pnl
            self.exposure = max(0, self.exposure - work.get('size', 0))
            # Log trade close
            self._log_audit('trades_closed', {
                'worker_id': self.worker_id,
                'pair': pair,
                'close_price': work.get('close_price'),
                'pnl': pnl,
                'reason': work.get('reason')
            })
        
        # Update Redis
        self._update_status()
        
        return result
    
    def _log_audit(self, event_type, data):
        """Log trade event to audit trail"""
        data['timestamp'] = datetime.now().isoformat()
        self.redis.lpush(f'audit:{event_type}', json.dumps(data))
    
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