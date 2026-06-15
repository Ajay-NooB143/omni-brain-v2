VPS_CONFIG = {
    'master': {
        'vps_ip': 'your_master_ip.com',  # Change this
        'ssh_user': 'root',
        'redis_port': 6379
    },
    'workers': {
        'worker-1': {
            'vps_ip': 'your_worker1_ip.com',  # Change this
            'pairs': ['EURUSD', 'GBPUSD', 'AUDUSD']
        },
        'worker-2': {
            'vps_ip': 'your_worker2_ip.com',  # Change this
            'pairs': ['XAUUSD', 'USOIL']
        },
        'worker-3': {
            'vps_ip': 'your_worker3_ip.com',  # Change this
            'pairs': ['BTC', 'ETH', 'BNB', 'SOL']
        }
    },
    'redis': {
        'host': 'your_master_ip.com',  # Same as master
        'port': 6379
    }
}