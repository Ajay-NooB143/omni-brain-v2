import json
import os
import time
import redis


def get_redis_connection(host=None, port=None, password=None, max_retries=3):
    """Redis connection with retry + exponential backoff

    Credentials resolved in order:
      1. explicit params (host/port/password)
      2. REDIS_HOST / REDIS_PORT / REDIS_PASSWORD env vars
      3. creds:redis hash in Redis itself (bridge bootstrap)
    """
    host = host or os.getenv('REDIS_HOST')
    port = port or (int(os.getenv('REDIS_PORT')) if os.getenv('REDIS_PORT') else None)
    password = password or os.getenv('REDIS_PASSWORD')

    if not host or not port:
        try:
            import urllib.request
            bridge_url = os.getenv('BRIDGE_URL', '').rstrip('/')
            if bridge_url:
                req = urllib.request.Request(f'{bridge_url}/config/redis')
                resp = urllib.request.urlopen(req, timeout=5)
                data = json.loads(resp.read())
                host = host or data.get('host', 'localhost')
                port = port or int(data.get('port', 6379))
                password = password or data.get('password', '')
        except Exception:
            pass

    host = host or 'localhost'
    port = port or 6379

    for attempt in range(max_retries):
        try:
            r = redis.Redis(
                host=host, port=port, password=password,
                decode_responses=True, socket_timeout=5
            )
            r.ping()
            return r
        except (redis.ConnectionError, redis.TimeoutError) as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise ConnectionError(f"Redis unavailable after {max_retries} attempts: {e}")


def validate_signal(signal_dict):
    """Validate required signal fields"""
    required = ['pair', 'direction', 'entry', 'size']
    for field in required:
        if field not in signal_dict or signal_dict[field] is None:
            raise ValueError(f"Missing required field: {field}")
    if signal_dict['direction'] not in ['BUY', 'SELL']:
        raise ValueError("Direction must be BUY or SELL")
    if signal_dict['size'] <= 0:
        raise ValueError("Size must be > 0")
    return True
