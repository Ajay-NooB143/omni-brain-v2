import time
import signal
import sys
import logging
import os
from dotenv import load_dotenv
from master_bot import MasterOrchestrator, AuditSystem
from redis_utils import get_redis_connection

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

running = True

def shutdown(sig, frame):
    global running
    logger.info(f"Received signal {sig}, shutting down gracefully...")
    running = False

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

def main():
    logger.info("=" * 80)
    logger.info("Starting Master Orchestrator")
    logger.info("=" * 80)

    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', '6379'))
    account_balance = float(os.getenv('ACCOUNT_BALANCE', 10000))
    max_daily_loss = float(os.getenv('MAX_DAILY_LOSS', 5.0))

    master = MasterOrchestrator(
        redis_host=redis_host,
        redis_port=redis_port,
        account_balance=account_balance
    )
    audit = AuditSystem(redis_host=redis_host, redis_port=redis_port)

    workers = {
        'worker-1': {
            'pairs': ['EURUSD', 'GBPUSD', 'AUDUSD'],
            'account': 3333.33
        },
        'worker-2': {
            'pairs': ['XAUUSD', 'USOIL'],
            'account': 3333.33
        },
        'worker-3': {
            'pairs': ['BTC', 'ETH', 'BNB', 'SOL'],
            'account': 3333.34
        }
    }

    for worker_id, config in workers.items():
        result = master.register_worker(
            worker_id=worker_id,
            pairs=config['pairs'],
            account_allocation=config['account'],
            max_daily_loss=2.0
        )
        logger.info(f"Registered: {result}")

    logger.info(f"All {len(workers)} workers registered")

    iteration = 0
    while running:
        try:
            iteration += 1

            status = master.get_cluster_status()

            audit.log_worker_status({
                'worker_id': 'CLUSTER',
                'daily_pl': status['total_daily_pl'],
                'open_trades': sum(w['trades'] for w in status['health']['workers'].values()),
                'exposure': status['risk']['total_exposure'],
                'drawdown': status['risk']['max_drawdown']
            })

            cb = status['circuit_breaker']
            if cb['circuit_breaker'] == 'ON':
                logger.critical("CLUSTER CIRCUIT BREAKER TRIGGERED!")
                audit.log_circuit_breaker({
                    'type': 'CLUSTER',
                    'triggered_id': 'ALL_WORKERS',
                    'reason': f"Loss {status['risk']['loss_percent']:.1f}%",
                    'action': 'STOP_ALL'
                })

            for worker_alert in cb['triggered_workers']:
                logger.warning(f"Worker CB: {worker_alert['worker_id']}")
                audit.log_circuit_breaker({
                    'type': 'WORKER',
                    'triggered_id': worker_alert['worker_id'],
                    'reason': f"Loss {worker_alert['loss_percent']:.1f}%",
                    'action': 'PAUSE'
                })

            logger.info(
                f"Cluster: {status['health']['cluster_status']} | "
                f"Workers: {len(status['health']['workers'])} | "
                f"Exposure: {status['risk']['exposure_percent']:.1f}% | "
                f"P&L: ${status['total_daily_pl']:.2f}"
            )

            for worker_id, worker_status in status['health']['workers'].items():
                logger.info(
                    f"  {worker_id}: {worker_status['status']} | "
                    f"Trades: {worker_status['trades']} open | "
                    f"P&L: ${worker_status['daily_pl']:.2f}"
                )

            time.sleep(60)

        except Exception as e:
            logger.error(f"Master error: {e}", exc_info=True)
            time.sleep(5)

    logger.info("Master orchestrator stopped")

if __name__ == '__main__':
    main()
