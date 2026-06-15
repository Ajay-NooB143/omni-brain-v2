import os
import time
import logging
from dotenv import load_dotenv
from worker_bot import WorkerBot

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

def main():
    worker_id = os.getenv('WORKER_ID')
    pairs = os.getenv('PAIRS', '').split(',')
    account = float(os.getenv('ACCOUNT_BALANCE', '3333.33'))
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', '6379'))
    
    logger.info(f"Starting {worker_id} for pairs: {pairs}")
    
    worker = WorkerBot(
        worker_id=worker_id,
        pairs=pairs,
        account_balance=account,
        redis_host=redis_host
    )
    
    logger.info(f"Worker initialized, connecting to Redis at {redis_host}")
    
    iteration = 0
    while True:
        try:
            iteration += 1
            
            work = worker.fetch_assigned_work()
            
            if work:
                logger.info(f"Processing work: {work.get('work_id')} for {work.get('pair')}")
                result = worker.execute_work(work, {})
                logger.info(f"Work result: {result}")
            
            if iteration % 30 == 0:
                status = worker.report_status()
                logger.info(f"Status update: {status['daily_pl']}, {status['open_trades']} open trades")
            
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"Worker error: {e}", exc_info=True)
            time.sleep(5)

if __name__ == '__main__':
    main()