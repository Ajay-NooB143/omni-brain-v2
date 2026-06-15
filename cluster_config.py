"""OmniBrain V2 — Cluster Configuration

Maps VPS IPs to worker roles and pair assignments

BEFORE DEPLOYMENT:
Replace all XX.XX.XX.{1,2,3,4} with your actual VPS IPs

Example:
  Master:   185.100.87.1
  Worker-1: 185.100.87.2
  Worker-2: 185.100.87.3
  Worker-3: 185.100.87.4
"""

import os


def get_redis_password():
    """Read from env, fallback to default (for local testing only)."""
    return os.getenv('REDIS_PASSWORD', 'L9zarK6YoCN18zcNKk6UKe3VanxcE3QBTVcQ13Xoyrk=')


# ============================================
# VPS CONFIGURATION
# ============================================

VPS_CONFIG = {
    'master': {
        'vps_ip': '172.105.252.194',
        'redis_port': 6379,
        'redis_password': get_redis_password(),
        'account_balance': 10000,
        'max_daily_loss': 5.0,
        'role': 'orchestrator'
    },
    'workers': {
        'worker-1': {
            'vps_ip': 'XX.XX.XX.2',  # ← REPLACE WITH WORKER-1 IP
            'redis_host': '172.105.252.194',
            'pairs': ['EURUSD', 'GBPUSD', 'AUDUSD'],
            'account_balance': 3333.33,
            'max_daily_loss': 2.0,
            'role': 'forex'
        },
        'worker-2': {
            'vps_ip': 'XX.XX.XX.3',  # ← REPLACE WITH WORKER-2 IP
            'redis_host': '172.105.252.194',
            'pairs': ['XAUUSD', 'USOIL'],
            'account_balance': 3333.33,
            'max_daily_loss': 2.0,
            'role': 'commodities'
        },
        'worker-3': {
            'vps_ip': 'XX.XX.XX.4',  # ← REPLACE WITH WORKER-3 IP
            'redis_host': '172.105.252.194',
            'pairs': ['BTC', 'ETH', 'BNB', 'SOL'],
            'account_balance': 3333.34,
            'max_daily_loss': 2.0,
            'role': 'crypto'
        }
    }
}


# ============================================
# HELPER FUNCTIONS
# ============================================

def get_master_config():
    """Return master node configuration."""
    return VPS_CONFIG['master']


def get_worker_config(worker_id):
    """Return configuration for a specific worker."""
    if worker_id not in VPS_CONFIG['workers']:
        raise ValueError(f"Unknown worker: {worker_id}")
    return VPS_CONFIG['workers'][worker_id]


def get_all_workers():
    """Return list of all worker IDs."""
    return list(VPS_CONFIG['workers'].keys())


def get_redis_host():
    """Return master Redis host IP."""
    return VPS_CONFIG['master']['vps_ip']


def validate_config():
    """Validate that all IPs are configured (not placeholders)."""
    errors = []

    # Check master IP
    if VPS_CONFIG['master']['vps_ip'].startswith('XX.XX.XX'):
        errors.append("Master IP is still a placeholder (XX.XX.XX.1)")

    # Check worker IPs
    for worker_id, config in VPS_CONFIG['workers'].items():
        if config['vps_ip'].startswith('XX.XX.XX'):
            errors.append(f"{worker_id} IP is still a placeholder")
        if config['redis_host'].startswith('XX.XX.XX'):
            errors.append(f"{worker_id} redis_host is still a placeholder")

    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
        print("\nEdit cluster_config.py and replace XX.XX.XX.{1,2,3,4} with real IPs")
        return False

    return True


# ============================================
# DEPLOYMENT REFERENCE
# ============================================

DEPLOYMENT_STEPS = """OMNIBRAIN V2 DEPLOYMENT CHECKLIST

1. UPDATE IPs IN THIS FILE
   Edit cluster_config.py:
   - Master:   XX.XX.XX.1 -> your_master_ip
   - Worker-1: XX.XX.XX.2 -> your_worker1_ip
   - Worker-2: XX.XX.XX.3 -> your_worker2_ip
   - Worker-3: XX.XX.XX.4 -> your_worker3_ip

2. DEPLOY MASTER VPS
   ssh root@your_master_ip
   cd /home/omni-brain-v2
   bash deploy_master.sh

3. DEPLOY WORKER VPS (repeat for each)
   ssh root@your_worker1_ip
   cd /home/omni-brain-v2
   WORKER_ID=worker-1 PAIRS=EURUSD,GBPUSD,AUDUSD bash deploy_worker.sh

   ssh root@your_worker2_ip
   WORKER_ID=worker-2 PAIRS=XAUUSD,USOIL bash deploy_worker.sh

   ssh root@your_worker3_ip
   WORKER_ID=worker-3 PAIRS=BTC,ETH,BNB,SOL bash deploy_worker.sh

4. VERIFY CLUSTER
   From master VPS:
   redis-cli -a "L9zarK6YoCN18zcNKk6UKe3VanxcE3QBTVcQ13Xoyrk=" SMEMBERS workers:active
   # Should return: worker-1, worker-2, worker-3

5. SEND TEST SIGNAL
   redis-cli -a "L9zarK6YoCN18zcNKk6UKe3VanxcE3QBTVcQ13Xoyrk=" RPUSH queue:worker-1 \
   '{"work_id":"test-001","pair":"EURUSD","action":"OPEN","direction":"BUY","size":1.5,"entry":1.095}'

6. MONITOR
   redis-cli -a "L9zarK6YoCN18zcNKk6UKe3VanxcE3QBTVcQ13Xoyrk=" MONITOR
"""


# ============================================
# OUTPUT
# ============================================

if __name__ == '__main__':
    print("OmniBrain V2 Cluster Configuration")
    print("=" * 60)
    print()

    if validate_config():
        print("Configuration valid")
        print()
        print("Master:")
        print(f"  IP: {VPS_CONFIG['master']['vps_ip']}")
        print(f"  Account: ${VPS_CONFIG['master']['account_balance']}")
        print()
        print("Workers:")
        for worker_id, config in VPS_CONFIG['workers'].items():
            print(f"  {worker_id} ({config['role']})")
            print(f"    IP: {config['vps_ip']}")
            print(f"    Pairs: {', '.join(config['pairs'])}")
            print(f"    Account: ${config['account_balance']}")
        print()
    else:
        print()
        print("Edit cluster_config.py before deployment")
