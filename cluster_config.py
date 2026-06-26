"""OmniBrain V2 — Cluster Configuration
All credentials stored in Redis, not hardcoded here.
Uses redis_bridge.py to fetch configs at runtime.

DEPLOYMENT:
  1. Set REDIS_HOST/REDIS_PORT/REDIS_PASSWORD in .env
  2. Run: python3 seed_credentials.py
  3. Config flows from Redis to all VPS instances
"""
import json
import os
from redis_bridge import get_vps_config, get_all_worker_ids, get_api_key, get_broker_config, get_cluster_config


def get_redis_password():
    return os.getenv('REDIS_PASSWORD') or getattr(get_redis_creds_safe(), 'password', '')


def get_redis_creds_safe():
    try:
        from redis_bridge import get_redis_creds
        return get_redis_creds()
    except Exception:
        return {}


VPS_CONFIG_CACHE = None


def _load_config():
    global VPS_CONFIG_CACHE
    if VPS_CONFIG_CACHE is not None:
        return VPS_CONFIG_CACHE

    master = get_vps_config('master')
    workers = {}
    for wid in get_all_worker_ids():
        try:
            workers[wid] = get_vps_config(wid)
        except ValueError:
            pass

    VPS_CONFIG_CACHE = {'master': master, 'workers': workers}
    return VPS_CONFIG_CACHE


def get_master_config():
    return _load_config()['master']


def get_worker_config(worker_id):
    config = _load_config()
    if worker_id not in config['workers']:
        raise ValueError(f"Unknown worker: {worker_id}")
    return config['workers'][worker_id]


def get_all_workers():
    return list(_load_config()['workers'].keys())


def get_redis_host():
    return _load_config()['master'].get('redis_host', 'localhost')


def validate_config():
    try:
        cfg = _load_config()
        errors = []
        if cfg['master']['ip'].startswith('XX.XX.XX'):
            errors.append("Master IP is still a placeholder")
        for wid, wc in cfg['workers'].items():
            if wc['ip'].startswith('XX.XX.XX'):
                errors.append(f"{wid} IP is still a placeholder")
        if errors:
            print("Configuration errors (update via Redis):")
            for e in errors:
                print(f"  - {e}")
            print("  Fix: HSET creds:vps:<role> ip '1.2.3.4'")
            return False
        return True
    except Exception as e:
        print(f"Config load error: {e}")
        print("Run seed_credentials.py first or check Redis connection.")
        return False


DEPLOYMENT_STEPS = """OMNIBRAIN V2 — REDIS BRIDGE DEPLOYMENT

1. SEED REDIS (one time, on master VPS):
   source .env && python3 seed_credentials.py --api-key 'sk-ant-...'

2. START BRIDGE SERVER (on master VPS):
   python3 bridge_server.py
   Or via start.sh: bash start.sh bridge

3. REGISTER WORKER VPS (from each worker VPS):
   curl -X POST http://<MASTER_IP>:8765/register \\
     -H 'X-API-Key: <key>' \\
     -d '{"role":"worker-1","ip":"<WORKER_IP>","pairs":["EURUSD","GBPUSD","AUDUSD"]}'

4. START WORKERS (on each VPS):
   bash start.sh master   # on master
   bash start.sh worker-1 # on worker-1
"""


if __name__ == '__main__':
    print("OmniBrain V2 — Cluster Configuration (Redis Bridge)")
    print("=" * 60)
    print()
    try:
        cfg = _load_config()
        print(f"Master: {cfg['master'].get('ip', 'unknown')}")
        print(f"  Account: ${cfg['master'].get('account_balance', '?')}")
        print()
        print("Workers:")
        for wid, wc in cfg['workers'].items():
            pairs = wc.get('pairs', [])
            if isinstance(pairs, str):
                pairs = json.loads(pairs)
            print(f"  {wid} ({wc.get('role', '?')})")
            print(f"    IP: {wc.get('ip', '?')}")
            print(f"    Pairs: {', '.join(pairs)}")
            print(f"    Account: ${wc.get('account_balance', '?')}")
    except Exception as e:
        print(f"Error: {e}")
        print("Run: python3 seed_credentials.py")
