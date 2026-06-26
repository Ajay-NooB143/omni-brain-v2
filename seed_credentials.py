#!/usr/bin/env python3
"""OmniBrain V2 — Seed Credentials into Redis
Run ONCE on the first master deployment to populate Redis with initial configs.
After seeding, credentials live ONLY in Redis — not in Python files.

Usage:
  python3 seed_credentials.py
  python3 seed_credentials.py --api-key 'sk-ant-xxxx' --broker-host '1.2.3.4'
"""
import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()
from redis_bridge import seed_default_credentials, set_credential


def main():
    parser = argparse.ArgumentParser(description='Seed credentials into Redis bridge')
    parser.add_argument('--api-key', help='Anthropic/OpenRouter API key')
    parser.add_argument('--telegram-token', help='Telegram bot token')
    parser.add_argument('--instagram-token', help='Instagram access token')
    parser.add_argument('--broker-host', help='MT5 Windows VPS IP or hostname')
    parser.add_argument('--broker-port', type=int, default=8765, help='MT5 bridge port')
    parser.add_argument('--broker-login', help='MT5 login')
    parser.add_argument('--broker-password', help='MT5 password')
    parser.add_argument('--broker-server', help='MT5 server name')
    parser.add_argument('--redis-password', help='Redis password (if not in .env)')
    args = parser.parse_args()

    seed_default_credentials(redis_password=args.redis_password)

    if args.api_key:
        set_credential('creds:api', 'anthropic_key', args.api_key)
        set_credential('creds:api', 'openrouter_key', args.api_key)
        print("  API key set")
    if args.telegram_token:
        set_credential('creds:api', 'telegram_bot_token', args.telegram_token)
        print("  Telegram token set")
    if args.instagram_token:
        set_credential('creds:api', 'instagram_token', args.instagram_token)
        print("  Instagram token set")
    if args.broker_host:
        set_credential('creds:broker', 'host', args.broker_host)
        set_credential('creds:broker', 'port', str(args.broker_port))
        print(f"  Broker host set to {args.broker_host}:{args.broker_port}")
        if args.broker_login:
            set_credential('creds:broker', 'login', args.broker_login)
        if args.broker_password:
            set_credential('creds:broker', 'password', args.broker_password)
        if args.broker_server:
            set_credential('creds:broker', 'server', args.broker_server)

    print("\nDone. Credentials are stored in Redis.")
    print("  Verify: redis-cli -a '<password>' HGETALL creds:redis")
    print("  Verify: redis-cli -a '<password>' HGETALL creds:vps:master")
    print("  Verify: redis-cli -a '<password>' HGETALL creds:api")


if __name__ == '__main__':
    main()
