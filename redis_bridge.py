"""OmniBrain V2 — Redis Credential Bridge
All secrets and configs stored in Redis, not in Python files.
"""
import json
import os
from redis_utils import get_redis_connection


_redis = None
_cache = {}


def _get_r():
    global _redis
    if _redis is None:
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', '6379'))
        password = os.getenv('REDIS_PASSWORD')
        _redis = get_redis_connection(host=host, port=port, password=password)
    return _redis


def get_vps_config(role='master'):
    """Fetch VPS config from Redis for a given role (master, worker-1, etc.)"""
    key = f'creds:vps:{role}'
    data = _get_r().hgetall(key)
    if not data:
        raise ValueError(f"No VPS config found in Redis for role='{role}'. Run seed_credentials.py first.")
    if 'pairs' in data:
        data['pairs'] = json.loads(data['pairs'])
    return data


def get_redis_creds():
    """Fetch Redis connection credentials from Redis itself (bootstrap)."""
    data = _get_r().hgetall('creds:redis')
    if data:
        return {
            'host': data.get('host', 'localhost'),
            'port': int(data.get('port', 6379)),
            'password': data.get('password'),
        }
    return {'host': 'localhost', 'port': 6379, 'password': None}


def get_api_key(name):
    """Fetch a specific API key from creds:api hash."""
    return _get_r().hget('creds:api', name) or os.getenv(name.upper())


def get_broker_config():
    """Fetch MT5 broker bridge config from Redis."""
    data = _get_r().hgetall('creds:broker')
    return {
        'host': data.get('host', os.getenv('WINDOWS_VPS_IP', '')),
        'port': int(data.get('port', 8765)),
        'login': data.get('login', ''),
        'password': data.get('password', ''),
        'server': data.get('server', ''),
    }


def get_cluster_config():
    """Fetch cluster-wide settings from Redis."""
    data = _get_r().hgetall('config:cluster')
    return {
        'master_id': data.get('master_id', 'master-prod'),
        'trading_mode': data.get('trading_mode', 'paper'),
        'initial_capital': float(data.get('initial_capital', 10)),
        'max_daily_loss': float(data.get('max_daily_loss', 1.0)),
    }


def get_all_worker_ids():
    """Get list of registered worker IDs from Redis."""
    raw = _get_r().get('config:workers')
    if raw:
        return json.loads(raw)
    return ['worker-1', 'worker-2', 'worker-3']


def set_credential(key_hash, field, value):
    """Set a single credential field in Redis."""
    _get_r().hset(key_hash, field, value)


def seed_default_credentials(redis_password=None):
    """Populate Redis with default credentials. Only run once on fresh deploy."""
    r = _get_r()
    r.hset('creds:redis', mapping={
        'host': os.getenv('REDIS_HOST', 'localhost'),
        'port': os.getenv('REDIS_PORT', '6379'),
        'password': redis_password or os.getenv('REDIS_PASSWORD', ''),
    })
    r.hset('creds:vps:master', mapping={
        'ip': os.getenv('VPS_IP', '172.105.252.194'),
        'redis_host': os.getenv('REDIS_HOST', 'localhost'),
        'redis_port': os.getenv('REDIS_PORT', '6379'),
        'account_balance': os.getenv('ACCOUNT_BALANCE', '10000'),
        'max_daily_loss': os.getenv('MAX_DAILY_LOSS', '5.0'),
        'role': 'orchestrator',
    })
    for wid, pairs, bal in [
        ('worker-1', ['EURUSD', 'GBPUSD', 'AUDUSD'], 3333.33),
        ('worker-2', ['XAUUSD', 'USOIL'], 3333.33),
        ('worker-3', ['BTC', 'ETH', 'BNB', 'SOL'], 3333.34),
    ]:
        r.hset(f'creds:vps:{wid}', mapping={
            'ip': os.getenv(f'{wid.upper()}_IP', '172.105.252.194'),
            'redis_host': os.getenv('REDIS_HOST', 'localhost'),
            'redis_port': os.getenv('REDIS_PORT', '6379'),
            'pairs': json.dumps(pairs),
            'account_balance': str(bal),
            'max_daily_loss': '2.0',
            'role': 'forex' if wid == 'worker-1' else ('commodities' if wid == 'worker-2' else 'crypto'),
        })
    r.set('config:workers', json.dumps(['worker-1', 'worker-2', 'worker-3']))
    r.hset('config:cluster', mapping={
        'master_id': 'master-prod',
        'trading_mode': 'paper',
        'initial_capital': '10',
        'max_daily_loss': '1.0',
    })
    print("Default credentials seeded into Redis.")
    print("Set API keys: HSET creds:api anthropic_key 'sk-ant-...'")
    print("Set broker:   HSET creds:broker host 'WINDOWS_VPS_IP' port 8765 login '' password '' server ''")


def clear_cache():
    _cache.clear()
