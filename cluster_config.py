VPS_CONFIG = {
    'master': {
        'vps_ip': 'YOUR_MASTER_IP',        # Replace with actual IP
        'ssh_user': 'root',
        'redis_port': 6379
    },
    'workers': {
        'worker-1': {
            'vps_ip': 'YOUR_WORKER1_IP',   # Replace with actual IP
            'pairs': ['EURUSD', 'GBPUSD', 'AUDUSD'],
            'account': 3333.33
        },
        'worker-2': {
            'vps_ip': 'YOUR_WORKER2_IP',   # Replace with actual IP
            'pairs': ['XAUUSD', 'USOIL'],
            'account': 3333.33
        },
        'worker-3': {
            'vps_ip': 'YOUR_WORKER3_IP',   # Replace with actual IP
            'pairs': ['BTC', 'ETH', 'BNB', 'SOL'],
            'account': 3333.34
        }
    },
    'redis': {
        'host': 'YOUR_MASTER_IP',          # Same as master
        'port': 6379,
        'password': 'L9zarK6YoCN18zcNKk6UKe3VanxcE3QBTVcQ13Xoyrk='
    }
}
