#!/usr/bin/env python3
import os
import time
import signal
import sys
from datetime import datetime
from redis_utils import get_redis_connection

r = get_redis_connection()

running = True

def shutdown(sig, frame):
    global running
    running = False

signal.signal(signal.SIGTERM, shutdown)
signal.signal(signal.SIGINT, shutdown)

def clear_screen():
    os.system('clear' if os.name == 'posix' else 'cls')

while running:
    clear_screen()

    print("=================================================================")
    print("              OMNIBRAIN V2 - LIVE P&L TICKER")
    print("=================================================================")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-----------------------------------------------------------------")

    total_pl = 0
    total_trades = 0

    for i, w in enumerate(['worker-1', 'worker-2', 'worker-3'], 1):
        pl = float(r.hget(f'worker:{w}', 'daily_pl') or 0)
        loss = float(r.hget(f'worker:{w}', 'daily_loss') or 0)
        trades = int(r.hget(f'worker:{w}', 'open_trades') or 0)
        status = r.hget(f'worker:{w}', 'status') or 'UNKNOWN'
        total_pl += pl
        total_trades += trades

        color = '\033[92m' if pl >= 0 else '\033[91m'
        reset = '\033[0m'

        print(f"  W{i}: {color}${pl:8.2f}{reset} | Loss: ${loss:6.2f} | Trades: {trades} | {status}")

    print("-----------------------------------------------------------------")
    print(f"  TOTAL: ${total_pl:8.2f} | Open Trades: {total_trades}")
    print(f"  Circuit Breaker: {r.hget('master:orchestrator', 'circuit_breaker') or 'OFF'}")
    print("=================================================================")
    print("\n  Press Ctrl+C to stop")

    time.sleep(2)
